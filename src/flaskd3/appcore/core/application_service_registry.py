from flaskd3.types.application_service import ApplicationService
from flaskd3.common.exceptions import InvalidStateException
from flaskd3.common.utils.common_utils import search_class


class ApplicationServiceRegistry(object):
    def __init__(self, modules, repo_registry, job_service):
        self.application_registry = search_class(
            modules=modules,
            sub_module_name=None,
            class_filters=[ApplicationService],
            exclude_list=[],
            get_object=True,
            obj_parameters=dict(repo_registry=repo_registry, job_service=job_service),
        )

    def get_service(self, name):
        service = self.application_registry.get(name)
        if not service:
            raise InvalidStateException(description="Queried service {} not found.".format(name))
        return service
