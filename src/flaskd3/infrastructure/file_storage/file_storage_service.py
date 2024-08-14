from flaskd3.infrastructure.file_storage.storage_locations.local_server_file_storage import (
    LocalServerFileStorage,
)
from flaskd3.common.constants import FileStorageLocation


class FileStorageService:

    storage_handler_map = {
        FileStorageLocation.LOCAL: LocalServerFileStorage,
    }

    def __init__(self, app_config, additional_configs=None):
        if not additional_configs:
            additional_configs = dict()
        self.handler_registry = dict()
        for storage_location in app_config.get("SUPPORTED_STORAGE_LOCATIONS"):
            self.handler_registry[storage_location] = FileStorageService.storage_handler_map.get(storage_location)(
                app_config, additional_configs.get(storage_location.value)
            )

    def get_handler(self, storage_location):
        return self.handler_registry.get(storage_location)

    def register_storage_handler(self, file_storage_handler):
        self.storage_handler_map[file_storage_handler.STORAGE_TYPE] = file_storage_handler
