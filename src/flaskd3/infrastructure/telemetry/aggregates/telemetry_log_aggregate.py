from datetime import datetime

from flaskd3.common.utils.id_generator_utils import simple_id_generator
from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.type_info import TypeInfo
from flaskd3.infrastructure.telemetry.value_objects import TelemetryLog, ErrorLog
from flaskd3.infrastructure.telemetry.constants import TelemetryLogLevel


class TelemetryLogAggregate(BaseEntity):
    telemetry_id = TypeInfo(str, primary_key=True)
    started_at = TypeInfo(datetime)
    user_id = TypeInfo(str)
    request_id = TypeInfo(str)
    url = TypeInfo(str)
    logs = TypeInfo(TelemetryLog, many=True)
    headers = TypeInfo(dict)
    payload = TypeInfo(dict)
    response = TypeInfo(dict, required=False)
    exception = TypeInfo(ErrorLog)

    def init(self, **kwargs):
        self._salt = 0

    def _log(self, log_level, message, data, entity_id=None, entity_name=None, key_tag=None, tags=None):
        self._salt += 1
        log_entry_id = simple_id_generator(self._salt)
        self.logs.add(TelemetryLog(log_entry_id=log_entry_id, log_level=log_level, message=message, log_data=data,
                                   entity_id=entity_id, entity_name=entity_name, key_tag=key_tag, tags=tags))

    def warn(self, message, data, entity_id=None, entity_name=None, key_tag=None, tags=None):
        self._log(TelemetryLogLevel.WARN, message, data, entity_id, entity_name, key_tag, tags)

    def info(self, message, data, entity_id=None, entity_name=None, key_tag=None, tags=None):
        self._log(TelemetryLogLevel.INFO, message, data, entity_id, entity_name, key_tag, tags)

    def debug(self, message, data, entity_id=None, entity_name=None, key_tag=None, tags=None):
        self._log(TelemetryLogLevel.DEBUG, message, data, entity_id, entity_name, key_tag, tags)

    def error(self, message, data, entity_id=None, entity_name=None, key_tag=None, tags=None):
        self._log(TelemetryLogLevel.ERROR, message, data, entity_id, entity_name, key_tag, tags)

    def log_exception(self, message, developer_message, stacktrace, error_code, response_code):
        self.exception = ErrorLog(response_code=response_code, message=message, developer_message=developer_message,
                                stacktrace=stacktrace, error_code=error_code)

    def set_response(self, response):
        self.response = response

    def set_user_id(self, user_id):
        self.user_id = user_id
