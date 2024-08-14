import abc
from flaskd3.types.constants import CoreDataTypes
from flaskd3.types.list_object import ListObject
from flaskd3.types.map_object import MapObject
from flaskd3.types.set_object import SetObject
from flaskd3.types.value_object import ValueObject


class MutableValueObject(ValueObject):

    core_type = CoreDataTypes.MUTABLE_VALUE_OBJECT

    _is_dirty = False

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __setattr__(self, key, value):
        if not key.startswith("_"):
            if self._is_frozen:
                self._is_dirty = True
        object.__setattr__(self, key, value)

    @property
    def is_dirty(self):
        if self._is_dirty:
            return self._is_dirty
        for arg, type_info in self._attributes_type_info.items():
            value = getattr(self, arg)
            if value is not None and isinstance(value, (ListObject, SetObject, MutableValueObject, MapObject)):
                if value.is_dirty:
                    return True
        return False

    def dirty(self):
        if self._is_dirty:
            return self.dict()
        else:
            return None

    @classmethod
    def from_dict(cls, dict_obj):
        if dict_obj is None:
            return None
        return cls(**dict_obj)

    def dict(self):
        dict_obj = dict()
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                dict_obj[key] = value
        return dict_obj

    def data(self):
        return self.dict()
