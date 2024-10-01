from datetime import datetime

from marshmallow import Schema, fields
from marshmallow.decorators import post_load

from flaskd3.appcore.core.api_docs import ma_plugin
from flaskd3.appcore.core.schema_manager import SchemaManager
from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.base_enum import BaseEnum
from flaskd3.types.value_object import BitMaskValueObject, ValueObject
from flaskd3.common.exceptions import InvalidStateException
from flaskd3.common.utils.common_utils import (
    convert_key_to_camel_case,
    convert_key_to_snake_case,
    to_camel_case,
)
from flaskd3.common.utils.json_utils import make_jsonify_ready


class BaseSchema(Schema):
    class Meta:
        dateformat = "iso"
        datetimeformat = "iso"

    @classmethod
    def get_name(cls):
        return cls.__name__.split("Schema")[0]


class VersionMixinSchema(object):
    version = fields.Integer(required=True, description="version of the booking")


class MultiTenantMixinSchema(object):
    tenantId = fields.String(attribute="tenant_id")


class ResourceVersionMixinSchema(object):
    resourceVersion = fields.Integer(required=True, description="resource version of the entity")


class LoadShallowMixinSchema(object):
    loadShallow = fields.Boolean(
        attribute="load_shallow",
        required=False,
        description="loaded Entities will be shallow if set to true",
    )


class ValueObjectSchema(BaseSchema):
    @property
    def value_object_class(self):
        raise AttributeError(f"Attribute: value_object_class not implemented for {self.get_name()}")

    @post_load
    def get_value(self, data, **kwargs):
        return self.value_object_class.from_dict(data) if data is not None else None


#@ma_plugin.map_to_openapi_type(fields.String)
class EnumField(fields.Field):
    def __init__(self, enum_class, **kwargs):
        if not issubclass(enum_class, BaseEnum):
            raise ValueError("Not a valid enum class")
        self.enum_class = enum_class
        self.many = kwargs.get("many", False)
        super(EnumField, self).__init__(**kwargs)

    default_error_messages = {
        "invalid-object": "Not a valid enum object.",
        "invalid-value": "Not a valid enum value.",
    }

    def _serialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        if self.many:
            return [entry.value for entry in value]
        else:
            if not isinstance(value, BaseEnum):
                self.fail("invalid-object")
            return value.value

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            if self.many:
                return [self.enum_class(entry) for entry in value]
            else:
                return self.enum_class(value)
        except ValueError:
            self.fail("invalid-value")


#@ma_plugin.map_to_openapi_type(fields.Raw)
class RawField(fields.Field):
    def _serialize(self, value, attr, data, **kwargs):
        return convert_key_to_camel_case(make_jsonify_ready(value))

    def _deserialize(self, value, attr, data, **kwargs):
        return convert_key_to_snake_case(value)


class BitMaskValueObjectField(fields.List):
    def __init__(self, bitmask_value_object_class, **kwargs):
        if not issubclass(bitmask_value_object_class, BitMaskValueObject):
            raise ValueError("Not a valid bit value object class")
        self.bitmask_value_object_class = bitmask_value_object_class
        self.many = True
        super(BitMaskValueObjectField, self).__init__(EnumField(bitmask_value_object_class.enum_class), **kwargs)

    default_error_messages = {
        "invalid-object": "Not a valid bitmask value object.",
        "invalid-value": "Not a valid bitmask value object value.",
    }

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        if not isinstance(value, self.bitmask_value_object_class):
            self.fail("invalid-object")
        return value.data()

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return self.bitmask_value_object_class.from_dict(value)
        except ValueError:
            self.fail("invalid-value")


class AutoGenerateSchema(BaseSchema):
    for_class = None
    exclude_keys = list()
    init_done = False
    field_class_override_map = dict()

    type_map = {
        int.__name__: fields.Integer,
        str.__name__: fields.String,
        datetime.__name__: fields.DateTime,
    }

    @classmethod
    def get_or_create_value_object_schema(cls, value_object_cls):
        vo_name = value_object_cls.get_name()
        schema_obj = SchemaManager.get_schema_obj(vo_name)
        if schema_obj:
            return schema_obj.__class__
        schema_class_name = "{}Schema".format(vo_name)
        value_object_schema_class = type(schema_class_name, (cls,), {"for_class": value_object_cls})
        value_object_schema_class.init_schema()
        return value_object_schema_class

    @classmethod
    def generate_schema(cls, for_class):
        if cls.init_done:
            return
        if not isinstance(cls.for_class, (BaseEntity, ValueObject)):
            raise InvalidStateException(message="Class mapping missing for Auto Schema: {}".format(cls.__name__))
        for key, type_info in cls.for_class.get_attributes():
            if key in cls.exclude_keys:
                continue
            if isinstance(type_info.class_obj, BaseEnum):
                filed_object = EnumField(
                    type_info.class_obj, required=type_info.required, many=type_info.many, attribute=key, description=type_info.description
                )
            elif isinstance(type_info.class_obj, (BaseEntity, ValueObject)):
                schema_class = cls.schema_map.get(key)
                if not schema_class and isinstance(type_info.class_obj, ValueObject):
                    schema_class = cls.get_or_create_value_object_schema(type_info.class_obj)
                if not schema_class:
                    raise InvalidStateException(message="Schema missing for key {} so cannot generate schema: {}".format(key, cls.__name__))
                filed_object = fields.Nested(schema_class, required=type_info.required, many=type_info.many, attribute=key)
            else:
                field_class = cls.field_class_override_map.get(key)
                if not field_class:
                    field_class = cls.type_map.get(type_info.class_obj.__name__)
                filed_object = field_class(required=type_info.required, many=type_info.many, attribute=key)
            setattr(cls, to_camel_case(key), filed_object)
        cls.init_done = True
