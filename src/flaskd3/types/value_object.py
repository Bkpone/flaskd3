from collections import defaultdict
from copy import copy
from datetime import datetime, time
from functools import wraps

from flaskd3.types.base_enum import BaseEnum
from flaskd3.types.constants import CoreDataTypes
from flaskd3.types.list_object import ListObject
from flaskd3.types.map_object import MapObject
from flaskd3.types.set_object import SetObject
from flaskd3.types.type_info import ValueObjectField
from flaskd3.common.exceptions import ValidationException
from flaskd3.common.utils.dateutils import parse_datetime, parse_time


class ValueObject(object):
    _is_frozen = False
    _init_overridden = False
    _parent_attributes = None
    core_type = CoreDataTypes.VALUE_OBJECT

    @classmethod
    def get_name(cls):
        return cls.__name__


    @classmethod
    def get_attributes(cls):
        attributes_type_info = dict()
        attributes = dict()
        attributes.update(cls.__dict__)
        if cls._parent_attributes:
            attributes.update(cls._parent_attributes)
        for key, field in attributes.items():
            if isinstance(field, ValueObjectField):
                attributes_type_info[key] = field
        return attributes_type_info

    @staticmethod
    def init_decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._is_frozen = True

        return wrapper

    def __new__(cls, *args, **kwargs):
        if not cls._init_overridden:
            cls.__init__ = ValueObject.init_decorator(cls.__init__)
            cls._init_overridden = True
            if not hasattr(cls, "data"):
                cls.data = cls.dict
        instance = object.__new__(cls)
        return instance

    def __init__(self, **kwargs):
        cls_ = type(self)
        self._attributes_type_info = cls_.get_attributes()
        class_attr_copy = self._attributes_type_info.copy()
        for arg, value in kwargs.items():
            field_info = class_attr_copy.pop(arg, None)
            if not field_info:
                raise TypeError("%r is an invalid keyword argument for %s" % (arg, self.__class__.__name__))
            if field_info.mapped:
                if not isinstance(value, dict):
                    raise TypeError("%r should be of type dict %s found" % (arg, self.__class__.__name__))
                value = MapObject(field_info.class_obj, value)
            elif field_info.many:
                values = [self._parse_value(v, field_info) for v in value] if value else list()
                if field_info.unique:
                    value = SetObject(field_info.class_obj, values)
                else:
                    value = ListObject(field_info.class_obj, values)
            else:
                value = self._parse_value(value, field_info)
            if value is None:
                if field_info.default:
                    value = field_info.get_default_value()
                elif not field_info.allow_none:
                    raise ValidationException("{} cannot be null for {}".format(arg, self.__class__.__name__))
            setattr(self, arg, value)
        for arg, field_info in class_attr_copy.items():
            if field_info.mapped:
                value = MapObject(field_info.class_obj)
            elif field_info.many:
                if field_info.unique:
                    value = SetObject(field_info.class_obj)
                else:
                    value = ListObject(field_info.class_obj)
            else:
                if field_info.required and field_info.default is None:
                    raise ValidationException("{} is a required field for {}".format(arg, self.__class__.__name__))
                value = field_info.get_default_value()
            if not value and not field_info.allow_none:
                raise ValidationException("{} cannot be null for {}".format(arg, self.__class__.__name__))
            setattr(self, arg, value)
        self.init(**kwargs)
        self._is_frozen = True

    def _parse_value(self, value, field_info):
        if isinstance(value, field_info.class_obj):
            return value
        if field_info.parser:
            return field_info.parser(value)
        if issubclass(field_info.class_obj, datetime):
            return parse_datetime(value)
        if issubclass(field_info.class_obj, BaseEnum):
            return field_info.class_obj(value)
        if issubclass(field_info.class_obj, ValueObject):
            return field_info.class_obj.from_dict(value)
        if isinstance(value, dict):
            return field_info.class_obj(**value)
        if issubclass(field_info.class_obj, time):
            return parse_time(value)
        if value is None:
            return None
        return field_info.class_obj(value)

    def __setattr__(self, key, value):
        if self._is_frozen and not key.startswith("_"):
            raise AttributeError("cannot set attribute in value object %s" % self.__class__.__name__)
        object.__setattr__(self, key, value)

    def __copy__(self):
        attributes = dict()
        for key, value in self.get_attributes().items():
            val = getattr(self, key)
            new_val = copy(val)
            attributes[key] = new_val
        return self.__class__(**attributes)

    def init(self, **kwargs):
        pass

    def dict(self):
        dict_obj = dict()
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                dict_obj[key] = value
        return dict_obj

    @property
    def is_dirty(self):
        return False

    def dirty(self):
        return dict()

    @classmethod
    def from_dict(cls, dict_obj):
        if dict_obj is None:
            return None
        if isinstance(dict_obj, dict):
            return cls(**dict_obj)
        return cls(dict_obj)


class BitMaskValueObject(ValueObject):

    enum_class = None

    def __init__(self, values):
        self.values_map = defaultdict(lambda: False)
        self.raw = 0
        for value in values:
            self.add(value)

    def __hash__(self):
        return hash(self.raw)

    def __contains__(self, item):
        if not isinstance(item, self.enum_class):
            item = self.enum_class(item)
        return self.values_map[item]

    def __eq__(self, other):
        if isinstance(other, BitMaskValueObject):
            return other.raw == self.raw
        return other == self

    def add(self, item):
        if not isinstance(item, self.enum_class):
            item = self.enum_class(item)
        self.raw = self.raw | item.bit_mask
        self.values_map[item] = True

    def remove(self, item):
        if not isinstance(item, self.enum_class):
            item = self.enum_class(item)
        self.raw = self.raw ^ item.bit_mask
        self.values_map[item] = False

    def dict(self):
        return self.raw

    def data(self):
        return [value.value for value, present in self.values_map.items() if present]

    def overlap(self, other):
        return self.raw & other.raw

    def is_subset(self, other):
        for key, value in self.values_map:
            if value and key not in other:
                return False
        return True

    @classmethod
    def from_dict(cls, values):
        if isinstance(values, int):
            values = [item for item in cls.enum_class if values & item.bit_mask > 0]
        return cls(values)
