import logging
from flaskd3.infrastructure.database.base_db_service import BaseDBService
from flaskd3.infrastructure.database.elasticsearch.elastic_search import ElasticSearch

logger = logging.getLogger(__name__)


class ElasticSearchService(BaseDBService):
    def __init__(self):
        self.elasticsearch = ElasticSearch()

    def init(self, app, config):
        self.elasticsearch.init(config)

    def get_db(self):
        return self.elasticsearch

    def rollback(self):
        pass

    def init_transaction(self):
        pass

    def commit(self):
        pass
