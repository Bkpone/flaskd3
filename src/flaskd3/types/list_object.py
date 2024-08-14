from flaskd3.types.constants import CoreDataTypes
from flaskd3.types.iter_base import IterBase
from flaskd3.common.utils.common_utils import convert_to_type


class ListObject(IterBase):

    core_type = CoreDataTypes.LIST

    def __init__(self, class_obj, items=None):
        self._class_obj = class_obj
        self._items = list()
        if items:
            for item in items:
                if not isinstance(item, self._class_obj):
                    item = convert_to_type(item, self._class_obj)
                    if not item:
                        raise AttributeError("Items can only be of type %s in ListObject" % self._class_obj.__name__)
                self._items.append(item)
        self._new_entries = list()
        self._deleted_entries = list()

    def __len__(self):
        return len(self._items)

    def get(self, index):
        return self._items[index]

    def add(self, item):
        if not isinstance(item, self._class_obj):
            raise AttributeError("Items can only be of type %s in ListObject" % self._class_obj.__name__)
        if item in self._deleted_entries:
            self._deleted_entries.remove(item)
        else:
            self._new_entries.append(item)
        self._items.append(item)

    def remove(self, item):
        if not isinstance(item, self._class_obj):
            raise AttributeError("Items can only be of type %s in ListObject" % self._class_obj.__name__)
        try:
            self._new_entries.remove(item)
        except ValueError:
            self._items.remove(item)
            self._deleted_entries.append(item)

    def clear(self):
        self._deleted_entries.clear()
        self._deleted_entries = self._items
        self._items = list()

    def __iter__(self):
        for i in self._items:
            yield i

    def list(self):
        return self._items

    def data(self):
        return self._items

    def dirty(self):
        if not self.is_dirty:
            return None
        return dict(
            type=self.core_type.value,
            data=dict(deleted=self._deleted_entries, added=self._new_entries),
        )

    @property
    def is_dirty(self):
        return self._deleted_entries or self._new_entries
