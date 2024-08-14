import json
import logging

from flaskd3.appcore.core.request_parsers import RequestTypes
from flaskd3.infrastructure.telemetry.factories.telemetry_log_factory import TelemetryLogFactory

logger = logging.getLogger(__name__)


class TelemetryLoggerService:

    EXCLUDE_PATHS_APPROX = [
        "healthcheck", "php"
    ]

    EXCLUDE_PATHS_EXACT = [
        "/", "/information"
    ]

    def __init__(self, telemetry_log_repository):
        self._current_logger = None
        self.telemetry_log_repository = telemetry_log_repository

    def init_logger(self, request, request_id):
        path = None
        data = dict()
        headers = None
        if request:
            path = request.path
            headers = dict(request.headers)
            if request.content_type:
                request_type = RequestTypes.type_from_content_type(request.content_type)
                if (request_type == RequestTypes.JSON and request.content_length == 0) \
                        or (request_type == RequestTypes.MULTIPART):
                    data = dict()
                else:
                    data = getattr(request, request_type.value)
                if request_type in [RequestTypes.ARGS, RequestTypes.FORM]:
                    data = dict(data=data.to_dict())
        self._current_logger = TelemetryLogFactory.create_telemetry_log(path, request_id, headers, data)

    @property
    def logger(self):
        if not self._current_logger:
            self.init_logger(None, None)
        return self._current_logger

    def should_log(self, logger_aggregate):
        if not len(logger_aggregate.logs):
            return False
        if logger_aggregate.url:
            if logger_aggregate.url in self.EXCLUDE_PATHS_EXACT:
                return False
            for e in self.EXCLUDE_PATHS_APPROX:
                if e in logger_aggregate.url:
                    return False
        return True
    
    def flush(self):
        if self.should_log(self._current_logger):
            self.telemetry_log_repository.save(self._current_logger)
        self._current_logger = None

    
