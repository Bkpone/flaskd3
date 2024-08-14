import logging
from elasticsearch import Elasticsearch
from flaskd3.infrastructure.database.elasticsearch.elastic_config import ElasticConfig

logger = logging.getLogger(__name__)


class ElasticSearch(object):
    def __init__(self):
        self.es_client = None

    @property
    def session(self):
        return self.es_client

    def rollback(self):
        pass

    def init_transaction(self):
        pass

    def commit(self):
        pass

    def init(self, config):
        elastic_config = ElasticConfig(config) if config else ElasticConfig()
        try:
            if elastic_config.ELASTIC_USERNAME and elastic_config.ELASTIC_PASSWORD:
                self.es_client = Elasticsearch(
                    [elastic_config.ELASTIC_HOST],
                    http_auth=(
                        elastic_config.ELASTIC_USERNAME,
                        elastic_config.ELASTIC_PASSWORD,
                    ),
                    use_ssl=elastic_config.ELASTIC_USE_SSL,
                    verify_certs=elastic_config.ELASTIC_VERIFY_SSL,
                )
            else:
                self.es_client = Elasticsearch(
                    [elastic_config.ELASTIC_HOST],
                    use_ssl=elastic_config.ELASTIC_USE_SSL,
                    verify_certs=elastic_config.ELASTIC_VERIFY_SSL,
                )
        except Exception:
            logger.exception("Elasticsearch Initialization Failed.")
