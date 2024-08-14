import json
import logging

from flaskd3.infrastructure.error_tracker.factories.api_error_log_factory import (
    APIErrorLogFactory,
)
from flaskd3.infrastructure.error_tracker.services.api_error_log_rmq_publisher import (
    APIErrorLogRMQPublisher,
)


logger = logging.getLogger(__name__)


class ErrorLoggerService:
    def __init__(self, async_push_enabled):
        self._init_done = False
        self.publisher = None
        self.api_error_log_repository = None
        self.async_push_enabled = async_push_enabled

    def init(self, app, api_error_log_repository):
        if self.async_push_enabled:
            self.publisher = APIErrorLogRMQPublisher(app.config["RABBIT_MQ_URL"])
        self.api_error_log_repository = api_error_log_repository
        self._init_done = True

    def log_api_error(self, request, response_code, message, developer_message, stacktrace, error_code,
                      publish_async=False):
        if not self._init_done:
            logging.error("Error logger init not done.")
            return None

        payload = dict()

        if request.content_type == "application/json" and request.data:
            data_json = getattr(request, "json", None)
            if data_json:
                payload["json"] = data_json
        data_args = getattr(request, "args", None)
        if data_args:
            payload["args"] = data_args.to_dict()
        data_form = getattr(request, "form", None)
        if data_form:
            payload["form"] = data_form.to_dict()

        payload["full_url"] = request.url

        if payload:
            # drop sensitive info
            payload.pop("password", None)
            payload.pop("number", None)
            payload.pop("phone_number", None)
            payload.pop("address", None)
            payload.pop("user_name", None)
        error_log_aggregate = APIErrorLogFactory.create_log_entry(
            request.path,
            payload,
            response_code,
            message,
            developer_message,
            stacktrace,
            error_code,
        )
        if publish_async:
            if not self.async_push_enabled:
                logging.error("Async push of api error not enabled so cannot push async")
                return error_log_aggregate
            self.publisher.publish(error_log_aggregate)
        else:
            self.api_error_log_repository.save(error_log_aggregate)
        return error_log_aggregate
