import os
import shutil
from flaskd3.infrastructure.file_storage.file_storage_base import FileStorageBase
from flaskd3.common.constants import FileStorageLocation
from flaskd3.common.utils.common_utils import urljoin


class LocalServerFileStorage(FileStorageBase):

    STORAGE_TYPE = FileStorageLocation.LOCAL

    def __init__(self, app_config, configs=None):
        self.folder_home = app_config.get("SHARED_FILE_PATH")
        self.server_path = app_config.get("SERVER_PATH")
        super().__init__(app_config.get("TEMP_FOLDER_PATH"))

    def _get_path(self, file_name, folder):
        return os.path.join(self.folder_home, folder, file_name)

    def create_folder(self, folder, access_level):
        os.mkdir(os.path.join(self.folder_home, folder))

    def store_file(self, file_name, folder, source, in_cdn):
        shutil.copyfile(source, self._get_path(file_name, folder))
        return self.get_file_url(file_name, folder)

    def store_fileobj(self, file_name, file_type, folder, source, in_cdn, access_level):
        path = self._get_path(file_name, folder)
        with open(path, "wb") as f:
            shutil.copyfileobj(source, f)
            f.close()
        return self.get_file_url(file_name, folder)

    def fetch(self, file_name, folder, access_level):
        return self._get_path(file_name, folder)

    def get_file_url(self, file_name, folder, in_cdn=None):
        return urljoin(self.server_path, "wpl/v1/files", file_name.split(".", 1)[0])
