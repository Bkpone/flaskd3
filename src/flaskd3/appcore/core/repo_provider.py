from flaskd3.infrastructure.database.redis.geo_redis_repository import GeoRedisRepository
from flaskd3.infrastructure.database.sqlalchemy.sql_base_aggregate_repository import (
    SQLABaseAggregateRepository,
)
from flaskd3.infrastructure.database.elasticsearch.elastic_repository import (
    ElasticRepository,
)
from flaskd3.common.exceptions import InvalidStateException
from flaskd3.common.utils.common_utils import search_class


class RepoProvider(object):
    def __init__(self, modules, db_service_provider):
        self.repo_store = search_class(
            modules=modules,
            sub_module_name="repositories",
            class_filters=[
                SQLABaseAggregateRepository,
                GeoRedisRepository,
                ElasticRepository,
            ],
            exclude_list=["SQLABaseAggregateRepository", "SQLABaseRelationshipRepository", "BaseRedisRepository"],
            get_object=True,
            obj_parameters=dict(db_service_provider=db_service_provider),
        )

    def get_repo(self, name):
        repo = self.repo_store.get(name)
        if not repo:
            raise InvalidStateException(description="Queried repo {} not found.".format(name))
        return repo
