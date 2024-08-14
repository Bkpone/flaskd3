import logging

from flaskd3.infrastructure.database.base_db_service import BaseDBService
from flaskd3.infrastructure.database.redis.redis_store import RedisStore

logger = logging.getLogger(__name__)


class RedisDBService(BaseDBService):
    def rollback(self):
        pass

    def init_transaction(self):
        pass

    def commit(self):
        pass

    def __init__(self):
        self.redis_store = RedisStore()

    def init(self, app, config):
        self.redis_store.init(config)

    def get_db(self):
        return self.redis_store
