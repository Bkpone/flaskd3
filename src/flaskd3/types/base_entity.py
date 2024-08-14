from transitions.core import MachineError

from flaskd3.appcore.core.request_context import get_tenant_id
from flaskd3.types.base_enum import BaseEnum
from flaskd3.types.constants import CoreDataTypes
from flaskd3.types.entity_set_object import EntitySetObject
from flaskd3.types.iter_base import IterBase
from flaskd3.types.list_object import ListObject
from flaskd3.types.map_object import MapObject
from flaskd3.types.mutable_value_object import MutableValueObject
from flaskd3.types.set_object import SetObject
from flaskd3.types.type_info import TypeInfo
from flaskd3.common.exceptions import (
    AuthorizationException,
    InvalidStateException,
    ValidationException,
)
from flaskd3.common.value_objects import ActionLog


class BaseEntity(object):

    _init_done = False
    _initialized = False
    _version_updated = True
    _primary_key = None
    _state_machine = None
    _is_shallow = False
    _id_prefix = ""
    _actions = None
    _parent_attributes = None
    is_multi_tenant = False
    state_machine_factory = None
    core_type = CoreDataTypes.ENTITY

    def get_attribute_type_info(self):
        return self._attributes_type_info

    @classmethod
    def _get_dict_attributes(cls):
        attributes = dict()
        attributes.update(cls.__dict__)
        if cls._parent_attributes:
            attributes.update(cls._parent_attributes)
        return attributes

    @classmethod
    def get_primary_key(cls):
        cls._init_primary_key()
        return cls._primary_key

    @classmethod
    def get_attributes(cls, args=None):
        attributes_type_info = dict()
        for key, type_info in cls._get_dict_attributes().items():
            if isinstance(type_info, TypeInfo):
                if args:
                    type_info.set_class_obj_for_one_of(args)
                attributes_type_info[key] = type_info
        attributes_type_info["deleted"] = TypeInfo(bool, required=False, default=False)
        attributes_type_info["version"] = TypeInfo(int, required=False, default=1)
        if cls.is_multi_tenant:
            attributes_type_info["tenant_id"] = TypeInfo(str, required=True)
        return attributes_type_info

    @classmethod
    def get_child_entities(cls):
        child_entities = list()
        for key, type_info in cls._get_dict_attributes().items():
            if isinstance(type_info, TypeInfo):
                class_objs = type_info.get_class_objects()
                for class_obj in class_objs:
                    if issubclass(class_obj, BaseEntity):
                        child_entities.append(class_obj)
        return child_entities

    @classmethod
    def get_id_prefix(cls):
        return cls._id_prefix

    @classmethod
    def _init_primary_key(cls):
        if cls._primary_key:
            return
        primary_key = None
        for key, type_info in cls._get_dict_attributes().items():
            if isinstance(type_info, TypeInfo):
                if type_info.primary_key:
                    if primary_key:
                        raise AttributeError("%s can have only one primary key." % cls.__name__)
                    primary_key = key
        if not primary_key:
            raise AttributeError("%s has no primary key defined." % cls.__name__)
        cls._primary_key = primary_key

    def __init__(self, **kwargs):
        cls_ = type(self)
        cls_._init_primary_key()
        self._attributes_type_info = cls_.get_attributes(kwargs)
        class_attr_copy = self._attributes_type_info.copy()
        if "is_shallow" in kwargs:
            self._is_shallow = kwargs.pop("is_shallow", False)
        for arg, value in kwargs.items():
            type_info = class_attr_copy.pop(arg, None)
            if not type_info:
                raise InvalidStateException(description="Entity {} got invalid keyword argument: {}".format(self.__class__.__name__, arg))
            if type_info.setter and not type_info.many:
                value = type_info.setter(value)
            self._validate_attribute(arg, value, type_info)
            if type_info.many:
                if issubclass(type_info.class_obj, BaseEntity):
                    value = EntitySetObject(type_info.class_obj, value, type_info.more_attr) if not self._is_shallow else None
                else:
                    if type_info.unique:
                        value = SetObject(type_info.class_obj, value)
                    else:
                        value = ListObject(type_info.class_obj, value)
            elif type_info.mapped:
                value = MapObject(type_info.class_obj, value)
            setattr(self, arg, value)
        for arg, type_info in class_attr_copy.items():
            if type_info.many:
                if issubclass(type_info.class_obj, BaseEntity):
                    value = EntitySetObject(type_info.class_obj)
                else:
                    if type_info.unique:
                        value = SetObject(type_info.class_obj)
                    else:
                        value = ListObject(type_info.class_obj)
            elif type_info.mapped:
                value = MapObject(type_info.class_obj, dict())
            elif arg == "tenant_id":
                value = get_tenant_id()
            else:
                value = type_info.get_default_value()
            setattr(self, arg, value)
        self._dirty = dict()
        self._initialized = True
        self.init(**kwargs)

    def _validate_attribute(self, key, value, type_info):
        if not type_info:
            raise TypeError("%r is an invalid keyword argument for %s" % (key, self.__class__.__name__))
        if not value:
            if not type_info.allow_none and not self._is_shallow and issubclass(type_info.class_obj, BaseEntity):
                raise TypeError("%r cannot be none for %s" % (key, self.__class__.__name__))
        elif not type_info.many and not type_info.mapped:
            # TODO:: Add strict flag or covert in the fly
            if type(value) != type_info.class_obj and not isinstance(value, type_info.class_obj):
                raise TypeError("%r is invalid value for %s for %s" % (value, key, self.__class__.__name__))

    def __setattr__(self, name, value):
        if self._initialized and not name.startswith("_") and name not in ["deleted"]:
            if name in ["version"]:
                raise AttributeError("version is a ready-only attribute")
            type_info = self._attributes_type_info.get(name)
            self._validate_attribute(name, value, type_info)

            if self._is_shallow and issubclass(type_info.class_obj, (BaseEntity, EntitySetObject)):
                raise AttributeError("Cannot update value of %s as its shallow" % self.__class__.__name__)

            old = getattr(self, name)

            if old is not None:
                if isinstance(old, BaseEntity):
                    raise AttributeError(
                        "Cannot update value of %s type attribute in %s" % (type(type_info.class_obj.__name__), self.__class__.__name__)
                    )
                elif isinstance(old, (EntitySetObject, ListObject, SetObject, MapObject)):
                    old.update(value)
                    return
            dirty_entry = self._dirty.get(name)
            if dirty_entry:
                old = dirty_entry.get("old")
            if issubclass(type_info.class_obj, BaseEnum):
                core_type = CoreDataTypes.ENUM
            elif hasattr(type_info.class_obj, "core_type"):
                core_type = type_info.class_obj.core_type
            else:
                core_type = type_info.class_obj.__name__
            self._dirty[name] = dict(type=core_type, data=dict(old=old, new=value))
            self.update_version()
        self.__dict__[name] = value

    def update(self, update_data):
        for key, value in update_data.items():
            setattr(self, key, value)

    def update_version(self, force=False):
        if not self._version_updated:
            if force or self.is_dirty:
                self.__dict__["version"] += 1
                self._version_updated = True

    def get_latest_version(self):
        self.update_version()
        return self.version

    def reset_version_lock(self):
        self._version_updated = False

    def init(self, **kwargs):
        pass

    @property
    def is_dirty(self):
        if self._dirty:
            return True
        for arg, type_info in self._attributes_type_info.items():
            value = getattr(self, arg)
            if value is not None and isinstance(
                value,
                (
                    BaseEntity,
                    ListObject,
                    SetObject,
                    EntitySetObject,
                    MutableValueObject,
                    MapObject,
                ),
            ):
                if value.is_dirty:
                    return True
        return False

    def dirty(self):
        dirty_dict = dict(id=self.primary_id, type=self.core_type.value, name=self.entity_name())
        data = dict()
        for arg, type_info in self._attributes_type_info.items():
            value = getattr(self, arg)
            if value and isinstance(
                value,
                (
                    BaseEntity,
                    ListObject,
                    SetObject,
                    EntitySetObject,
                    MutableValueObject,
                    MapObject,
                ),
            ):
                arg_dirty_dict = value.dirty()
                if arg_dirty_dict:
                    data[arg] = arg_dirty_dict
            else:
                dirty_val = self._dirty.get(arg)
                if dirty_val:
                    data[arg] = dirty_val
        if not data:
            return None
        self.update_version(force=True)
        dirty_dict["data"] = data
        return dirty_dict

    def dict(self):
        self.update_version()
        response = dict()
        for arg, type_info in self._attributes_type_info.items():
            response[arg] = getattr(self, arg)
        return response

    def data(self):
        self.update_version()
        response = dict()
        for arg, type_info in self._attributes_type_info.items():
            if type_info.hidden:
                continue
            obj = getattr(self, arg)
            if isinstance(obj, (BaseEntity, IterBase)):
                obj = obj.data()
            response[arg] = obj
        response.pop("deleted", None)
        additional_attributes = self.get_additional_attributes()
        if additional_attributes:
            response.update(additional_attributes)
        if self.state_machine_factory is not None:
            if not self._state_machine:
                self._state_machine = self.state_machine_factory.build(self)
            response["transitions"] = self._state_machine.get_visible_transitions()
        return response

    @property
    def primary_key(self):
        return self._primary_key

    @property
    def primary_id(self):
        return getattr(self, self._primary_key)

    @property
    def primary_data(self):
        return {self._primary_key: getattr(self, self._primary_key)}

    def validate_entity(self):
        return True

    def delete(self):
        self.deleted = True
        for arg, type_info in self._attributes_type_info.items():
            value = getattr(self, arg)
            if value and isinstance(value, (BaseEntity, EntitySetObject)):
                value.delete()

    def update_one_of_attribute(self, selector_update, attribute_update):
        setattr(self, selector_update[0], selector_update[1])
        self._attributes_type_info[attribute_update[0]].set_class_obj_for_one_of(dict([selector_update]))
        setattr(self, attribute_update[0], attribute_update[1])

    @property
    def unique_name(self):
        name = self.__class__.__name__.lower().split("aggregate")
        if len(name) > 1:
            return name[0]
        return name[0].split("entity")[0]

    @classmethod
    def entity_name(cls):
        name = cls.__name__.lower().split("aggregate")
        if len(name) > 1:
            return name[0]
        return name[0].split("entity")[0]

    def act(self, action_request, user_roles=None):
        if not self._actions:
            self._actions = list()
        self._actions.append(action_request)
        if not self._state_machine:
            self._state_machine = self.state_machine_factory.build(self)
        if not self._state_machine.is_authorised(action_request.action, user_roles):
            raise AuthorizationException("User does not have the right privileges.")
        if hasattr(self, "action_log"):
            self.action_log.add(action_request)
        old_state = getattr(self, self._state_machine.state_key)
        try:
            getattr(self._state_machine, action_request.action.value)()
        except MachineError as e:
            raise ValidationException(message="Invalid state transition", description=str(e))
        self._actions.append(
            ActionLog(
                action_request=action_request.data(),
                old_state=old_state.value,
                new_state=getattr(self, self._state_machine.state_key).value,
            )
        )

    @property
    def has_actions(self):
        return self._actions is not None

    def get_actions_update(self):
        return dict(actions=self._actions, update=self.dirty())

    def get_additional_attributes(self):
        return None
