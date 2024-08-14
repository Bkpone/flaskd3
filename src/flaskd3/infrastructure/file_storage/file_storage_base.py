import abc
import os

from flaskd3.common.constants import FileAccessLevel, FileStorageLocation
from flaskd3.common.exceptions import ConfigurationError


class FileStorageBase:

    STORAGE_TYPE = FileStorageLocation.LOCAL
    PUBLIC_BUCKET = None
    PRIVATE_BUCKET = None
    PROTECTED_BUCKET = None

    def __init__(self, temp_folder_path):
        self.temp_folder_path = temp_folder_path

    @abc.abstractmethod
    def create_folder(self, folder):
        raise NotImplementedError("Implement create folder")

    @abc.abstractmethod
    def store_file(self, file_name, folder, source, in_cdn):
        pass

    @abc.abstractmethod
    def store_fileobj(self, file_name, file_type, folder, source, in_cdn, access_level):
        pass

    @abc.abstractmethod
    def fetch(self, file_name, folder, access_level):
        pass

    @abc.abstractmethod
    def get_file_url(self, file_name, folder, in_cdn):
        pass

    def get_temp_file_path(self, file, folder):
        file_path = "{}_{}_{}".format(self.STORAGE_TYPE.value, folder, file)
        return os.path.join(self.temp_folder_path, file_path)

    def get_bucket_name(self, access_level):
        bucket_name = None
        if access_level == FileAccessLevel.PUBLIC:
            bucket_name = self.PUBLIC_BUCKET
        elif access_level == FileAccessLevel.PRIVATE:
            bucket_name = self.PRIVATE_BUCKET
        elif access_level == FileAccessLevel.PROTECTED:
            bucket_name = self.PROTECTED_BUCKET
        else:
            raise ConfigurationError(description=f"Invalid access level: {access_level}")
        if bucket_name:
            return bucket_name
        raise ConfigurationError(description=f"Bucket not found for access level: {access_level}")
