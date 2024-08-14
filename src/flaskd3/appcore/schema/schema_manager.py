import inspect

import marshmallow

from flaskd3.common.utils.common_utils import get_sub_modules


class SchemaInfo:

    def __init__(self, name:str, class_obj, obj_instance):
        self.name = name
        self.class_obj = class_obj
        self.obj_instance = obj_instance


class SchemaManager:

    schema_map = dict()

    @classmethod
    def load_all_schemas(cls, serializers_module_parent):
        marshmallow_modules_found = set()
        serializer_modules = get_sub_modules(serializers_module_parent, suffix=".serializers")
        for serializer_module in serializer_modules:
            for name, class_obj in inspect.getmembers(serializer_module):
                if inspect.isclass(class_obj) and type(class_obj) == marshmallow.schema.SchemaMeta and name != "Schema" and name not in marshmallow_modules_found:
                    name = class_obj.get_name() if hasattr(class_obj, 'get_name') else class_obj.__name__
                    cls.schema_map[name] = SchemaInfo(name=name, class_obj=class_obj,
                                                      obj_instance=class_obj(unknown="EXCLUDE"))
                    marshmallow_modules_found.add(name)

    @classmethod
    def get_schema_map(cls):
        return cls.schema_map

    @classmethod
    def get_schema_obj(cls, name):
        schema_info = cls.schema_map.get(name)
        if not schema_info:
            return None
        return schema_info.obj_instance

    @classmethod
    def get_schema_obj_from_class(cls, schema_class):
        if not hasattr(schema_class, 'get_name'):
            return None
        name = schema_class.get_name()
        schema_info = cls.schema_map.get(name)
        if not schema_info:
            return None
        return schema_info.obj_instance
