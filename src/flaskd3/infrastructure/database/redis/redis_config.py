import os
import json


class RedisConfig:

    REDIS_IS_CLUSTER_MODE = os.environ.get("REDIS_IS_CLUSTER_MODE", False)
    REDIS_NODES = json.loads(os.environ.get("REDIS_NODES", '[{"host":"localhost", "port":6379}]'))

    def __init__(self, config):
        if config:
            self.REDIS_IS_CLUSTER_MODE = config["redis_is_cluster_mode"]
            self.REDIS_NODES = config["redis_nodes"]
