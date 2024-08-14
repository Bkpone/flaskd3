from flaskd3.common.utils.id_generator_utils import (
    extract_id_salt,
    simple_id_generator,
)
from flaskd3.types.constants import CoreDataTypes
from flaskd3.types.iter_base import IterBase

from flaskd3.types.base_enum import BaseEnum


class EntitySetObject(IterBase):

    core_type = CoreDataTypes.ENTITY_LIST

    class EntryType(BaseEnum):
        NEW = "new"
        DELETED = "deleted"
        OLD = "old"

    class ItemEntry(object):
        def __init__(self, item, entry_type):
            self.item = item
            self.entry_type = entry_type

    def __init__(self, class_obj, items=None, more_attr=None):
        self._class_obj = class_obj
        self._items = dict()
        self._max_id_salt = 0
        if more_attr:
            self.id_parts = more_attr.get("id_parts")
            if self.id_parts is None:
                self.id_parts = 2
        else:
            self.id_parts = 2
        if items:
            for item in items:
                if not isinstance(item, self._class_obj):
                    raise AttributeError("Items can only be of type %s in ListObject" % self._class_obj.__name__)
                id_salt = extract_id_salt(item.primary_id)
                if id_salt:
                    self._max_id_salt = max(id_salt, self._max_id_salt)
                else:
                    self._max_id_salt += 1
                self._items[item.primary_id] = EntitySetObject.ItemEntry(item, EntitySetObject.EntryType.OLD)

    def get(self, primary_id):
        entry = self._items.get(primary_id)
        if not entry:
            return None
        if entry and entry.entry_type == EntitySetObject.EntryType.DELETED:
            return None
        return entry.item

    def add(self, item):
        if isinstance(item, dict):
            if not item.get(self._class_obj.get_primary_key()):
                item[self._class_obj.get_primary_key()] = self.get_next_id()
            item = self._class_obj(**item)
        if not isinstance(item, self._class_obj):
            raise AttributeError("Items can only be of type %s in ListObject" % self._class_obj.__name__)
        self._max_id_salt += 1
        primary_id = item.primary_id
        entry = self._items.get(primary_id)
        if entry:
            if entry.entry_type in [
                EntitySetObject.EntryType.OLD,
                EntitySetObject.EntryType.NEW,
            ]:
                raise ValueError("Item already present in the list")
            entry.entry_type = EntitySetObject.EntryType.OLD
        else:
            self._items[primary_id] = EntitySetObject.ItemEntry(item, EntitySetObject.EntryType.NEW)
        return item

    @property
    def max_salt(self):
        return self._max_id_salt

    def remove(self, item_id):
        entry = self._items.get(item_id)
        if not entry:
            raise ValueError("Item not present in the list")
        if entry.entry_type == EntitySetObject.EntryType.NEW:
            self._items[item_id] = None
        else:
            entry.item.delete()
            entry.entry_type = EntitySetObject.EntryType.DELETED
        return entry.item

    def remove_missing(self, id_set):
        key_ids = list(self._items.keys())
        for i in key_ids:
            item_obj = self._items.get(i)
            if item_obj.entry_type != EntitySetObject.EntryType.DELETED:
                if item_obj.item.primary_id not in id_set:
                    self.remove(item_obj.item.primary_id)

    def __iter__(self):
        for i in self._items.values():
            if i.entry_type != EntitySetObject.EntryType.DELETED:
                yield i.item

    def get_next_id(self):
        return simple_id_generator(self._max_id_salt + 1, self.id_parts)

    def list(self):
        return [entry.item for entry in self._items.values()]

    def data(self):
        data = list()
        for i in self._items.values():
            if i.entry_type != EntitySetObject.EntryType.DELETED:
                data.append(i.item.data())
        return data

    def clear(self):
        for entry_id in self._items:
            if self._items[entry_id].entry_type == EntitySetObject.EntryType.NEW:
                self._items[entry_id] = None
            else:
                self._items[entry_id].item.delete()
                self._items[entry_id].entry_type = EntitySetObject.EntryType.DELETED

    def update(self, update_data):
        primary_key = self._class_obj.get_primary_key()
        id_set = set()
        for item in update_data:
            item_id = item.get(primary_key)
            if not item_id:
                item_obj = self.add(item)
                item_id = item_obj.primary_id
            else:
                item_obj = self.get(item_id)
                item_obj.update(item)
            id_set.add(item_id)
        self.remove_missing(id_set)

    @property
    def is_dirty(self):
        for entry in self._items.values():
            if entry.entry_type in [
                EntitySetObject.EntryType.NEW,
                EntitySetObject.EntryType.DELETED,
            ]:
                return True
            if entry.item.is_dirty:
                return True
        return False

    def delete(self):
        self.clear()

    def dirty(self):
        added = []
        deleted = []
        updated = []
        for entry in self._items.values():
            if entry.entry_type == EntitySetObject.EntryType.NEW:
                added.append(entry.item)
            elif entry.entry_type == EntitySetObject.EntryType.DELETED:
                deleted.append(entry.item)
            else:
                dirty = entry.item.dirty()
                if dirty:
                    updated.append(dirty)
        if not added and not deleted and not updated:
            return None
        return dict(
            type=self.core_type.value,
            data=dict(deleted=deleted, added=added, updated=updated),
        )

    def __len__(self):
        size = 0
        for i in self._items.values():
            if i.entry_type != EntitySetObject.EntryType.DELETED:
                size += 1
        return size
