import logging

from redis.client import Redis
from rediscluster.client import RedisCluster

from flaskd3.infrastructure.database.redis.redis_config import RedisConfig

logger = logging.getLogger(__name__)


class RedisStore(object):
    def __init__(self):
        self.redis_client = None

    @property
    def session(self):
        return self.redis_client

    def rollback(self):
        pass

    def init_transaction(self):
        pass

    def commit(self):
        pass

    def init(self, config):
        redis_config = RedisConfig(config)
        try:
            if redis_config.REDIS_IS_CLUSTER_MODE:
                nodes = redis_config.REDIS_NODES
                self.redis_client = RedisCluster(
                    startup_nodes=nodes,
                    decode_responses=True,
                    skip_full_coverage_check=True,
                )
            else:
                node = redis_config.REDIS_NODES[0]
                self.redis_client = Redis(**node)
        except Exception:
            logger.exception("Redis Initialization Failed.")
