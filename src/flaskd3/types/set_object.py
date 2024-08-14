from flaskd3.types.constants import CoreDataTypes
from flaskd3.types.iter_base import IterBase
from flaskd3.common.utils.common_utils import convert_to_type


class SetObject(IterBase):

    core_type = CoreDataTypes.SET

    def __init__(self, class_obj, items=None):
        self._class_obj = class_obj
        self._items = set()
        if items:
            for item in items:
                if not isinstance(item, self._class_obj):
                    item = convert_to_type(item, self._class_obj)
                    if not item:
                        raise AttributeError("Items can only be of type %s in SetObject" % self._class_obj.__name__)
                self._items.add(item)
        self._old = self._items.copy()

    def add(self, item):
        if not isinstance(item, self._class_obj):
            raise AttributeError("Items can only be of type %s in SetObject" % self._class_obj.__name__)
        self._items.add(item)

    def replace(self, item):
        if not isinstance(item, self._class_obj):
            raise AttributeError("Items can only be of type %s in SetObject" % self._class_obj.__name__)
        self._items.discard(item)
        self._items.add(item)

    def remove(self, item):
        if not isinstance(item, self._class_obj):
            raise AttributeError("Items can only be of type %s in SetObject" % self._class_obj.__name__)
        self._items.remove(item)

    def discard(self, item):
        self._items.discard(item)

    def issubset(self, other):
        if isinstance(other, SetObject):
            return self._items.issubset(other.list())
        else:
            return self._items.issubset(other)

    def get(self, item):
        raise AttributeError("get is not a valid function in set Object")

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for i in self._items:
            yield i

    def __contains__(self, item):
        return item in self._items

    def __str__(self):
        return str(self._items)

    def list(self):
        return self._items

    def data(self):
        return self._items

    def clear(self):
        self._items.clear()

    def _compute_dirty(self):
        added = self._items.difference(self._old)
        removed = self._old.difference(self._items)
        return added, removed

    def dirty(self):
        added, removed = self._compute_dirty()
        if not added and not removed:
            return None
        return dict(type=self.core_type.value, data=dict(added=added, removed=removed))

    @property
    def is_dirty(self):
        added, removed = self._compute_dirty()
        return added or removed
