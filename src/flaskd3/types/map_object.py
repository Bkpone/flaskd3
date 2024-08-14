from flaskd3.types.base_enum import BaseEnum
from flaskd3.types.constants import CoreDataTypes
from flaskd3.common.utils.common_utils import convert_to_type


class MapObject(object):

    core_type = CoreDataTypes.MAP

    class EntryType(BaseEnum):
        NEW = "new"
        DELETED = "deleted"
        OLD = "old"
        UPDATED = "updated"

    class ItemEntry(object):
        def __init__(self, entry_type, old_value=None):
            self.entry_type = entry_type
            self.old_value = old_value

    def __init__(self, class_obj, items=None):
        self._class_obj = class_obj
        self._items = dict()
        self._meta_data = dict()
        if items:
            for key, value in items.items():
                if not isinstance(value, self._class_obj):
                    if hasattr(self._class_obj, "from_dict"):
                        item = self._class_obj.from_dict(value)
                    else:
                        item = self._class_obj(value)

                else:
                    item = value
                self._items[key] = item
                self._meta_data[key] = MapObject.ItemEntry(MapObject.EntryType.OLD)

    def get(self, index):
        return self._items.get(index)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        if not isinstance(value, self._class_obj):
            value = convert_to_type(value, self._class_obj)
        item = self._meta_data.get(key)
        if not item or item.entry_type == MapObject.EntryType.NEW:
            self._meta_data[key] = MapObject.ItemEntry(MapObject.EntryType.NEW)
        else:
            self._meta_data[key] = MapObject.ItemEntry(MapObject.EntryType.UPDATED, self._items[key])
        self._items[key] = value

    def __delitem__(self, key):
        item = self._items.get(key)
        if not item:
            raise KeyError("item not present")
        else:
            self._meta_data[key] = MapObject.ItemEntry(MapObject.EntryType.DELETED, item)
            del self._items[key]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for key, value in self._items.items():
            yield key, value.item

    def dirty(self):
        added = dict()
        deleted = dict()
        updated = dict()
        for key, value in self._meta_data.items():
            if value.entry_type == MapObject.EntryType.NEW:
                added[key] = dict(old=None, new=self._items[key])
            elif value.entry_type == MapObject.EntryType.UPDATED:
                updated[key] = dict(old=value.old_value, new=self._items[key])
            elif value.entry_type == MapObject.EntryType.DELETED:
                deleted[key] = dict(old=value.old_value, new=None)

        return dict(
            type=self.core_type.value,
            data=dict(deleted=deleted, added=added, updated=updated),
        )

    @property
    def is_dirty(self):
        dirty = self.dirty()
        return dirty["data"]["deleted"] or dirty["data"]["added"] or dirty["data"]["updated"]

    def dict(self):
        return self._items

    def data(self):
        return self._items

    def update(self, new_data):
        keys = set(self._items.keys())
        for key, value in new_data.items():
            keys.discard(key)
            self[key] = value
        for key in keys:
            del self[key]

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def items(self):
        return self._items.items()
