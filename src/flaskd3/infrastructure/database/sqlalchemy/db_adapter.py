from collections import defaultdict
from datetime import datetime
from enum import Enum

from _pydecimal import Decimal

from flaskd3.appcore.core.request_context import get_tenant_id
from flaskd3.types.base_dto import BaseDto
from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.base_enum import BaseEnum
from flaskd3.types.entity_set_object import EntitySetObject
from flaskd3.types.list_object import ListObject
from flaskd3.types.map_object import MapObject
from flaskd3.types.mutable_value_object import MutableValueObject
from flaskd3.types.set_object import SetObject
from flaskd3.types.value_object import ValueObject
from flaskd3.common.constants import NOT_NONE
from flaskd3.common.errors import CommonError
from flaskd3.common.exceptions import AggregateNotFound, InvalidStateException
from flaskd3.common.money import Money
from flaskd3.common.utils import dateutils
from flaskd3.common.utils.json_utils import make_jsonify_ready


class DBAdapter(object):
    def __init__(self, entity_map, base_repo, exclude_key_map=None):
        self.entity_map = entity_map
        self.base_repo = base_repo
        self.exclude_key_map = exclude_key_map if exclude_key_map else dict()

    @staticmethod
    def get_model_attributes(model, excluded_attributes):
        attributes = dict()
        for attr_name, attr_val in model.__dict__.items():
            if attr_name.startswith("_"):
                continue
            if excluded_attributes and attr_name in excluded_attributes:
                continue
            attributes[attr_name] = attr_val
        return attributes

    def _update_model_map(self, models_map, entity_class, query_tuple, key_list):
        model_class = self.entity_map[entity_class.__name__]
        query_list = [getattr(model_class, query_tuple[0]).in_(query_tuple[1])]
        has_deleted_flag = getattr(model_class, "deleted", None)
        if has_deleted_flag:
            query_list.append(getattr(model_class, "deleted") == False)
        models = self.base_repo.filter(model_class, *query_list)
        if has_deleted_flag:
            query_list.pop()
        for model in models:
            keys = dict(entity_name=entity_class.__name__)
            for key in key_list:
                keys[key] = getattr(model, key)
            models_map[frozenset(keys.items())].append(model)

    def _load_all_models(self, entity_class, models_map, query_tuple, key_list):
        key_list_copy = key_list.copy()
        key_list_copy.append(entity_class.get_primary_key())
        for entity_class_obj in entity_class.get_child_entities():
            self._update_model_map(
                models_map, entity_class_obj, query_tuple, key_list_copy
            )
            self._load_all_models(
                entity_class_obj, models_map, query_tuple, key_list_copy
            )

    def _get_object(self, type_info, query_list, model_map, obj=None):
        if issubclass(type_info.class_obj, BaseEntity):
            return self.to_entities(
                entity_class=type_info.class_obj,
                query_list=query_list,
                model_map=model_map,
                many=type_info.many,
            )
        elif issubclass(type_info.class_obj, BaseEnum):
            if type_info.many:
                if obj:
                    return [type_info.class_obj(o) for o in obj]
                else:
                    return list()
            return type_info.class_obj(obj) if obj else obj
        elif issubclass(type_info.class_obj, datetime):
            if type_info.many:
                if obj:
                    return [dateutils.parse_datetime(o, should_localize=True) for o in obj]
                else:
                    return list()
            return dateutils.parse_datetime(obj, should_localize=True)
        elif issubclass(type_info.class_obj, Money):
            return Money(obj) if obj else obj
        elif type_info.mapped:
            return MapObject(type_info.class_obj, obj)
        elif issubclass(type_info.class_obj, (ValueObject, MutableValueObject)):
            if type_info.many:
                ret_obj = list()
                if obj:
                    for entry in obj:
                        ret_obj.append(type_info.class_obj.from_dict(entry))
                return ret_obj
            else:
                return type_info.class_obj.from_dict(obj) if obj is not None else obj
        else:
            return obj

    def _get_entity(
        self,
        model,
        entity_class,
        query_list,
        models_map,
        exclude_list=None,
        is_shallow=False,
    ):
        attr = dict(is_shallow=is_shallow)
        model_attributes = self.get_model_attributes(model, exclude_list)
        attribute_type_info = entity_class.get_attributes(model_attributes)
        if "created_at" not in attribute_type_info.keys():
            model_attributes.pop("created_at", None)
        if "modified_at" not in attribute_type_info.keys():
            model_attributes.pop("modified_at", None)
        list_type_attribute_info = getattr(model, "list_type_attribute_info", dict())
        for attribute_name, type_info in list_type_attribute_info.items():
            attr[attribute_name] = self.to_list_data(type_info, query_list)
        for attribute_name, type_info in attribute_type_info.items():
            if attribute_name in list_type_attribute_info.keys():
                continue
            obj = model_attributes.pop(attribute_name, None)
            attr[attribute_name] = self._get_object(
                type_info, query_list, models_map, obj
            )
        attr.update(model_attributes)
        entity = entity_class(**attr)
        entity.reset_version_lock()
        return entity

    def to_db_models_for_list_data(
        self, attrib_value, list_type_attribute, parent_key_dict=None,
            tenant_id=None
    ):
        models = list()
        if not parent_key_dict:
            parent_key_dict = dict()
        current_data = self.to_list_data(list_type_attribute, parent_key_dict)
        if getattr(list_type_attribute.model_class, "deleted", None):
            for entry in current_data:
                if entry not in attrib_value:
                    model_attributes = parent_key_dict.copy()
                    model_attributes[list_type_attribute.data_key] = entry
                    model_attributes["deleted"] = True
                    models.append(list_type_attribute.model_class(**model_attributes))
                else:
                    attrib_value.pop(entry)
        else:
            deleted_entries = list()
            for entry in current_data:
                if entry not in attrib_value:
                    model_attributes = parent_key_dict.copy()
                    if tenant_id:
                        model_attributes["tenant_id"] = tenant_id
                    model_attributes[list_type_attribute.data_key] = entry
                    deleted_entries.append(
                        list_type_attribute.model_class(**model_attributes)
                    )
                else:
                    attrib_value.pop(entry)
            self.base_repo.delete_all(deleted_entries)
        for entry in attrib_value:
            model_attributes = parent_key_dict.copy()
            if tenant_id:
                model_attributes["tenant_id"] = tenant_id
            model_attributes[list_type_attribute.data_key] = entry
            models.append(list_type_attribute.model_class(**model_attributes))
        return models

    def to_db_models(self, entity, parent_key_dict=None):
        try:
            exclude_keys = self.exclude_key_map.get(entity.__class__.__name__)
            exclude_keys = exclude_keys if exclude_keys else []
            model_class = self.entity_map[entity.__class__.__name__]
            list_type_attribute_info = getattr(
                model_class, "list_type_attribute_info", dict()
            )
            models = []
            attr = dict()
            primary_data = entity.primary_data.copy()
            if parent_key_dict:
                attr.update(parent_key_dict)
                primary_data.update(parent_key_dict)
            for attrib_key, attrib_value in entity.dict().items():
                if attrib_key in exclude_keys:
                    continue
                if list_type_attribute_info.get(attrib_key):
                    models.extend(
                        self.to_db_models_for_list_data(
                            attrib_value,
                            list_type_attribute_info.get(attrib_key),
                            primary_data
                        )
                    )
                    continue
                attribute_info = entity.get_attribute_type_info().get(attrib_key)

                if issubclass(attribute_info.class_obj, BaseEntity):
                    if attribute_info.many:
                        for entry in attrib_value.list():
                            models.extend(self.to_db_models(entry, primary_data))
                    else:
                        if attrib_value:
                            models.extend(self.to_db_models(attrib_value, primary_data))
                else:
                    attr[attrib_key] = DBAdapter.make_db_ready(attrib_value)
            model = model_class(**attr)
            models.append(model)
        except KeyError as e:
            raise InvalidStateException(
                error=CommonError.ENTITY_TO_DB_CONVERSION_MAP_MISSING,
                description=str(e),
            )
        except Exception as e:
            raise InvalidStateException(
                error=CommonError.ENTITY_TO_DB_CONVERSION_ERROR, description=str(e)
            )
        return models

    def to_list_data(self, list_data_info, query_list):
        try:
            if getattr(list_data_info.model_class, "deleted", None):
                query_list.update(deleted=False)
            models = self.base_repo.filter_by(list_data_info.model_class, **query_list)
            query_list.pop("deleted", None)
            return [getattr(model, list_data_info.data_key) for model in models]
        except KeyError as e:
            raise InvalidStateException(
                error=CommonError.ENTITY_TO_DB_CONVERSION_MAP_MISSING,
                description=str(e),
            )

    def to_entities(self, entity_class, query_list, model_map, many=False):
        try:
            entities = []
            model_map_key = [("entity_name", entity_class.__name__)]
            model_map_key.extend(query_list.items())
            models = model_map[frozenset(model_map_key)]
            for model in models:
                exclude_list = self.exclude_key_map.get(entity_class.__name__)
                if not exclude_list:
                    exclude_list = []
                exclude_list.extend(query_list.keys())
                new_query_dict = query_list.copy()
                primary_key = entity_class.get_primary_key()
                if primary_key:
                    new_query_dict[primary_key] = getattr(model, primary_key)
                entity = self._get_entity(
                    model, entity_class, new_query_dict, model_map, exclude_list
                )
                entities.append(entity)
        except KeyError as e:
            raise InvalidStateException(
                error=CommonError.ENTITY_TO_DB_CONVERSION_MAP_MISSING,
                description=str(e),
            )
        return entities if many else entities[0] if len(entities) > 0 else None

    def to_aggregate(self, model, aggregate_class, models_map, is_shallow):
        """

        :param model:
        :param aggregate_class:
        :param models_map:
        :param is_shallow:
        :return:
        """
        try:
            primary_key = aggregate_class.get_primary_key()
            query_list = {primary_key: getattr(model, primary_key)}
        except AttributeError:
            # Some aggregates don't have a primary key
            query_list = {}
        aggregate = self._get_entity(
            model,
            aggregate_class,
            query_list,
            models_map,
            exclude_list=self.exclude_key_map.get(aggregate_class.__name__),
            is_shallow=is_shallow,
        )
        return aggregate

    def load_aggregate(
        self,
        aggregate_class,
        aggregate_id,
        for_update=False,
        nowait=False,
        is_shallow=False,
    ):
        """

        :param aggregate_class:
        :param aggregate_id:
        :param for_update:
        :param nowait:
        :param is_shallow:
        :return:
        """
        try:
            query_list = dict()
            if aggregate_class.is_multi_tenant:
                query_list["tenant_id"] = get_tenant_id()
            query_list[aggregate_class.get_primary_key()] = aggregate_id
            model_class = self.entity_map[aggregate_class.__name__]
            if getattr(model_class, "deleted", None):
                query_list.update(deleted=False)
            if for_update:
                model = self.base_repo.get_for_update(
                    model_class, **query_list, nowait=nowait
                )
            else:
                model = self.base_repo.get(model_class, **query_list)
            if not model:
                raise AggregateNotFound(aggregate_class.entity_name(), aggregate_id)
            return self.load_aggregates_by_models(aggregate_class, [model], is_shallow)[
                0
            ]
        except KeyError as e:
            raise InvalidStateException(
                error=CommonError.ENTITY_TO_DB_CONVERSION_MAP_MISSING,
                description=str(e),
            )
        # except Exception as e:
        #     raise InvalidStateException(error=CommonError.ENTITY_TO_DB_CONVERSION_ERROR, description=str(e))

    def load_aggregates(
        self, aggregate_class, for_update, nowait, order_by, load_shallow, queries, meta
    ):
        """

        :param aggregate_class:
        :param for_update:
        :param nowait:
        :param order_by:
        :param load_shallow:
        :param queries:
        :return:
        """
        try:
            model_class = self.entity_map[aggregate_class.__name__]
            query_list = list()
            if aggregate_class.is_multi_tenant:
                query_list.append(getattr(model_class, "tenant_id") == get_tenant_id())
            if isinstance(queries, dict):
                for key, val in queries.items():
                    if isinstance(val, (list, set)):
                        query_list.append(getattr(model_class, key).in_(val))
                    elif val is None:
                        query_list.append(getattr(model_class, key).is_(None))
                    elif val == NOT_NONE:
                        query_list.append(getattr(model_class, key).isnot(None))
                    else:
                        query_list.append(getattr(model_class, key) == val)
            elif isinstance(queries, (list, tuple)):
                query_list.extend(queries)
            else:
                raise InvalidStateException(
                    description="Invalid queries type to load_aggregates"
                )
            if getattr(model_class, "deleted", None):
                query_list.append(model_class.deleted == False)
            models = self.base_repo.filter(
                model_class,
                *query_list,
                nowait=nowait,
                for_update=for_update,
                order_by=order_by,
                meta=meta
            )
            models = models.all()
            return self.load_aggregates_by_models(aggregate_class, models, load_shallow)
        except KeyError as e:
            raise InvalidStateException(
                error=CommonError.ENTITY_TO_DB_CONVERSION_MAP_MISSING,
                description=str(e),
            )

    def load_aggregates_by_models(self, aggregate_class, models, load_shallow):
        """

        :param aggregate_class:
        :param models:
        :param load_shallow:
        :return:
        """
        aggregates = []
        models_map = defaultdict(list)
        primary_key = aggregate_class.get_primary_key()
        if not load_shallow:
            self._load_all_models(
                aggregate_class,
                models_map,
                (primary_key, [getattr(model, primary_key) for model in models]),
                list(),
            )
        for model in models:
            aggregates.append(
                self.to_aggregate(model, aggregate_class, models_map, load_shallow)
            )
        return aggregates

    @staticmethod
    def make_db_ready(obj):
        if isinstance(obj, (list, set)):
            response_list = list()
            for item in obj:
                response_list.append(DBAdapter.make_db_ready(item))
            return response_list
        if isinstance(obj, dict):
            if not obj:
                return None
            return make_jsonify_ready(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, BaseEntity):
            return DBAdapter.make_db_ready(obj.dict())
        if isinstance(obj, (ValueObject, MutableValueObject)):
            return make_jsonify_ready(obj.dict())
        if isinstance(obj, EntitySetObject):
            return DBAdapter.make_db_ready(obj.list())
        if isinstance(obj, (ListObject, SetObject)):
            return make_jsonify_ready(obj.list())
        if isinstance(obj, BaseDto):
            return DBAdapter.make_db_ready(obj.data())
        if isinstance(obj, Money):
            return DBAdapter.make_db_ready(obj.to_dict())
        if isinstance(obj, MapObject):
            return DBAdapter.make_db_ready(obj.dict())
        return obj
