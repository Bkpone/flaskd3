from flaskd3.types.base_enum import BaseEnum


class CoreDataTypes(BaseEnum):
    ENTITY = "entity"
    SET = "set"
    LIST = "list"
    MAP = "map"
    ENTITY_LIST = "entity_list"
    VALUE_OBJECT = "value_object"
    MUTABLE_VALUE_OBJECT = "mutable_value_object"
    ENUM = "enum"
