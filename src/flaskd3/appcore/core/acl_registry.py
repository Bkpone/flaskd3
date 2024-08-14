from flaskd3.types.acl_service import ACLService
from flaskd3.common.exceptions import InvalidStateException
from flaskd3.common.utils.common_utils import search_class


class AntiCorruptionLayerRegistry(object):
    def __init__(self, modules):
        self.registry = search_class(
            modules=modules,
            sub_module_name=None,
            class_filters=[ACLService],
            exclude_list=[],
            get_object=True,
        )

    def get_service(self, name):
        service = self.registry.get(name)
        if not service:
            raise InvalidStateException(description="Queried acl {} not found.".format(name))
        return service
