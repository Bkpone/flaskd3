# coding=utf-8

import logging
import json
from flaskd3.infrastructure.database.base_repository import BaseRepository
from flaskd3.infrastructure.database.constants import DBType

logger = logging.getLogger(__name__)


class ElasticRepository(BaseRepository):
    def __init__(self, db_service_provider):
        self.elasticsearch = db_service_provider.get_db_service(DBType.NOSQL).get_db()

    def new_index(self, index_name, index_body):
        return self.elasticsearch.es_client.indices.create(index=index_name, body=index_body, request_timeout=10)

    def delete_index(self, index_name):
        return self.elasticsearch.es_client.indices.delete(index=index_name, request_timeout=10)

    def append(self, index_name, doc):
        return self.elasticsearch.es_client.index(index=index_name, body=doc, request_timeout=10)

    def append_multiple(self, index_name, docs):
        for doc in docs:
            self.elasticsearch.es_client.index(index=index_name, body=doc, request_timeout=10)
        return 0

    def get_all(self, index_name):
        return self.elasticsearch.es_client.search(body={"query": {"match_all": {}}}, index=index_name, request_timeout=10)

    def get(self, index_name, search_params):
        search_params = json.dumps(search_params)
        return self.elasticsearch.es_client.search(
            index=index_name,
            body=search_params,
            request_timeout=10,
            size=10000,
            _source=True,
        )

    def get_all_indices(self):
        return self.elasticsearch.es_client.indices.get_alias("*", request_timeout=10)

    def delete(self, index_name, key, value):
        return self.elasticsearch.es_client.delete_by_query(index=index_name, body={"query": {"match": {key: value}}})

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def session(self):
        return self.elasticsearch
