from flaskd3.appcore.core.acl_registry import AntiCorruptionLayerRegistry
from flaskd3.appcore.core.application_service_registry import ApplicationServiceRegistry
from flaskd3.infrastructure.infrastructure_service_registry import (
    InfrastructureServiceRegistry,
)
from flaskd3.infrastructure.telemetry.services.telemetry_logger_service import TelemetryLoggerService


class AppCore:
    def __init__(self):
        self.repo_provider = None
        self.infrastructure_service_registry = None
        self.application_service_registry = None
        self.job_service = None
        self.acl_registry = None
        self.telemetry_logger_service = None

    def init(self, app, application_service_modules, domain_modules, acl_modules):
        if not application_service_modules:
            application_service_modules = list()
        if not domain_modules:
            domain_modules = list()
        if not acl_modules:
            acl_modules = list()
        self.infrastructure_service_registry = InfrastructureServiceRegistry(app.config, domain_modules)
        self.infrastructure_service_registry.init(app)
        self.repo_provider = self.infrastructure_service_registry.get_repo_provider()
        self.job_service = self.infrastructure_service_registry.get_job_service()
        self.application_service_registry = ApplicationServiceRegistry(application_service_modules, self.repo_provider,
                                                                       self.job_service)
        self.acl_registry = AntiCorruptionLayerRegistry(acl_modules)
        self.telemetry_logger_service = TelemetryLoggerService(self.repo_provider.get_repo("telemetry_log_repository"))

    def get_application_service(self, name):
        return self.application_service_registry.get_service(name)

    def get_infra_service(self, name):
        return self.infrastructure_service_registry.get_service(name)

    def get_acl_service(self, name):
        return self.acl_registry.get_service(name)

    def get_repo(self, name):
        return self.repo_provider.get_repo(name)
    
    def get_telemetry_logger(self):
        return self.telemetry_logger_service


app_core = AppCore()
