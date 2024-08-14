# coding=utf-8
"""
Base Repository
"""
import logging

from flaskd3.infrastructure.database.base_repository import BaseRepository
from flaskd3.infrastructure.database.constants import DBType
from flaskd3.common.exceptions import RedisError

logger = logging.getLogger(__name__)


class RedisRepository(BaseRepository):
    """
    Base repository
    """

    def __init__(self, db_service_provider):
        self.redis_store = db_service_provider.get_db_service(DBType.REDIS).get_db()

    @property
    def name(self):
        return self.__class__.__name__

    def get_for_update(self, **kwargs):
        raise IndentationError("get for update not supported in redis")

    def delete(self, item):
        self.store.delete(item.primary_id)

    def delete_all(self, items):
        for item in items:
            self.delete(item)

    def session(self):
        pass

    def delete_by_query(self, **kwargs):
        raise IndentationError("delete_by_query not implemented")

    def filter_by(self, **kwargs):
        pass

    def filter(self, **kwargs):
        pass

    def get(self, key):
        """
        create new entry in table
        :param key:
        :return:
        """
        return self.store.get(key)

    def get_or_create(self, key, value):
        value = self.get(key)
        if not value:
            self.save(key, value)
        return value

    def save(self, aggregate):
        """
        :param key:
        :param data
        :return:
        """
        try:
            self.store.set(aggregate.primary_id, aggregate.data())
        except Exception as exp:
            logger.exception("RedisError")
            raise RedisError(exp.__str__())
        return aggregate

    def save_all(self, aggregates):
        for aggregate in aggregates:
            self.save(aggregate)
        return aggregates

    def update(self, item):
        return self.save(item)

    def update_all(self, items):
        for item in items:
            self.update(item)
        return items

    @property
    def store(self):
        return self.redis_store.session
