import importlib

from flaskd3.appcore.core.repo_provider import RepoProvider
from flaskd3.infrastructure.async_job_runner.services.job_service import JobService
from flaskd3.infrastructure.database.constants import DBType
from flaskd3.infrastructure.database.db_service_provider import DBServiceProvider
from flaskd3.infrastructure.database.elasticsearch.elastic_service import (
    ElasticSearchService,
)
from flaskd3.infrastructure.database.redis.redis_db_service import RedisDBService
from flaskd3.infrastructure.database.sqlalchemy.sql_db_service import SQLAlchemyDBService
from flaskd3.infrastructure.domain_events.services.domain_event_service import (
    DomainEventService,
)
from flaskd3.infrastructure.error_tracker.services.error_logger_service import (
    ErrorLoggerService,
)
from flaskd3.infrastructure.file_storage.file_storage_service import FileStorageService
from flaskd3.infrastructure.id_generator.id_generator_service import IDGeneratorService
from flaskd3.infrastructure.oauth.oauth_service import OAuthService
from flaskd3.common.exceptions import InvalidStateException
from flaskd3.infrastructure.secret_store.secret_store_provider import SecretStoreProvider


class InfrastructureServiceRegistry(object):

    @staticmethod
    def _init_db_service_provider():
        db_service_provider = DBServiceProvider()
        db_service_provider.register_db_service(DBType.RDS, SQLAlchemyDBService())
        db_service_provider.register_db_service(DBType.REDIS, RedisDBService())
        db_service_provider.register_db_service(DBType.NOSQL, ElasticSearchService())
        return db_service_provider

    def __init__(self, app_config, repo_locations):
        if not repo_locations:
            repo_locations = []
        repo_locations.append(importlib.import_module(__package__))
        self.infrastructure_registry = dict()
        db_service_provider = self._init_db_service_provider()
        self.infrastructure_registry["db_service_provider"] = db_service_provider
        self.repo_provider = RepoProvider(repo_locations, db_service_provider)
        self.infrastructure_registry["auth_infrastructure_service"] = OAuthService()
        self.infrastructure_registry["id_generator_infrastructure_service"] = IDGeneratorService(
            self.repo_provider.get_repo("id_generator_repository")
        )
        self.infrastructure_registry["domain_event_service"] = DomainEventService(
            self.repo_provider.get_repo("domain_event_repository"))
        self.infrastructure_registry["job_service"] = JobService(
            self.repo_provider.get_repo("job_repository"),
            self.repo_provider.get_repo("recurring_job_repository"),
        )
        self.infrastructure_registry["error_logger"] = ErrorLoggerService(async_push_enabled=False)
        secret_store_configs = app_config.get("SECRET_STORE_CONFIGS")
        secret_store_provider = SecretStoreProvider(secret_store_configs)
        self.infrastructure_registry["secret_store_provider"] = secret_store_provider
        self.infrastructure_registry["file_storage"] = FileStorageService(
            app_config,
            self.infrastructure_registry["secret_store_provider"].get_default().get_secret("cloud_storage_config"),
        )

    def init(self, app):
        self.get_service("auth_infrastructure_service").configure(app)
        sql_db_service = self.infrastructure_registry["db_service_provider"].get_db_service(DBType.RDS)
        db_config_location = app.config.get("DB_CONFIG_LOCATION", "")
        db_config_data = None
        if db_config_location == "config":
            db_config_data = app.config.get("DB_CONFIG")
        elif db_config_location == "secret_store":
            db_config_data = self.infrastructure_registry["secret_store_provider"].get_default().get_secret("db_config")
        sql_db_service.init(app, db_config_data)
        redis_config_location = app.config.get("REDIS_CONFIG_LOCATION", "")
        redis_config_data = None
        if redis_config_location == "config":
            redis_config_data = app.config.get("DB_CONFIG")
        elif redis_config_location == "secret_store":
            redis_config_data = self.infrastructure_registry["secret_store_provider"].get_default().get_secret(
                "redis_config")
        redis_service = self.infrastructure_registry["db_service_provider"].get_db_service(DBType.REDIS)
        redis_service.init(app, redis_config_data)
        sql_db_service = self.infrastructure_registry["db_service_provider"].get_db_service(DBType.RDS)
        db_config_location = app.config.get("DB_CONFIG_LOCATION", "")
        db_config_data = None
        if db_config_location == "config":
            db_config_data = app.config.get("DB_CONFIG")
        elif db_config_location == "secret_store":
            db_config_data = self.infrastructure_registry["secret_store_provider"].get_default().get_secret("db_config")
        sql_db_service.init(app, db_config_data)
        redis_config_location = app.config.get("REDIS_CONFIG_LOCATION", "")
        redis_config_data = None
        if redis_config_location == "config":
            redis_config_data = app.config.get("DB_CONFIG")
        elif redis_config_location == "secret_store":
            redis_config_data = self.infrastructure_registry["secret_store_provider"].get_default().get_secret(
                "redis_config")
        redis_service = self.infrastructure_registry["db_service_provider"].get_db_service(DBType.REDIS)
        redis_service.init(app, redis_config_data)
        error_logger_service = self.infrastructure_registry["error_logger"]
        error_logger_service.init(app, self.repo_provider.get_repo("api_error_log_repository"))

    def get_service(self, name):
        service = self.infrastructure_registry.get(name)
        if not service:
            raise InvalidStateException(description="Queried service {} not found.".format(name))
        return service

    def get_repo_provider(self):
        return self.repo_provider

    def get_job_service(self):
        return self.infrastructure_registry["job_service"]
