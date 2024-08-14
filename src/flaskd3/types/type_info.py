import inspect

from flaskd3.types.base_enum import BaseEnum


class TypeInfo(object):
    def __init__(
        self,
        class_obj=None,
        many=False,
        required=True,
        default=None,
        allow_none=True,
        primary_key=False,
        unique=False,
        setter=None,
        one_of=None,
        mapped=False,
        hidden=False,
        more_attr=None,
        description=None,
    ):
        self.class_obj = class_obj
        self.many = many
        self.default = default
        self.required = required
        self.allow_none = allow_none
        self.primary_key = primary_key
        self.setter = setter
        self.unique = unique
        self.mapped = mapped
        self.hidden = hidden
        self.description = description
        self.more_attr = more_attr
        if one_of and not isinstance(one_of, OneOf):
            raise AttributeError("invalid oneOf attribute value.")
        self.one_of = one_of

    def get_default_value(self):
        if inspect.isclass(self.default):
            value = self.default()
        else:
            value = self.default
        return value

    def set_class_obj_for_one_of(self, kwargs):
        if self.one_of:
            value = kwargs[self.one_of.selector_key]
            if isinstance(value, BaseEnum):
                value = value.value
            self.class_obj = self.one_of.mapping[value]

    def get_class_objects(self):
        return [self.class_obj] if not self.one_of else self.one_of.mapping.values()


class OneOf(object):
    def __init__(self, selector_key, mapping):
        self.selector_key = selector_key
        self.mapping = mapping


class ValueObjectField(object):
    def __init__(self, class_obj, required=True, default=None, allow_none=True, many=False, unique=False, parser=None, mapped=False):
        self.class_obj = class_obj
        self.default = default
        self.required = required
        self.allow_none = allow_none
        self.many = many
        self.unique = unique
        self.parser = parser
        self.mapped = mapped

    def get_default_value(self):
        if inspect.isclass(self.default):
            value = self.default()
        else:
            value = self.default
        return value
