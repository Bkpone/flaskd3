import re
import flask
import logging
import traceback

from flask import request

from marshmallow import ValidationError

from flaskd3.common.exceptions import (
    get_http_status_code_from_exception,
    DCException,
    ApiValidationException,
)
from flaskd3.appcore.core.application_core import app_core
from flaskd3.appcore.core.api_response_builder import ApiResponseBuilder


logger = logging.getLogger(__name__)


def exception_handler(error):
    """
    Exception handler
    :param error:
    :return:
    """
    if isinstance(error, DCException) or isinstance(error, ApiValidationException):
        status_code = get_http_status_code_from_exception(error)
        error_dict = dict(
            code=error.code,
            message=error.message,
            developer_message=error.description,
            extra_payload=error.extra_payload,
            request_id=flask.g.request_id,
        )
    else:
        # populate status code
        status_code = 500
        if getattr(error, "status_code", None):
            status_code = error.status_code
        if getattr(error, "code", None):
            status_code = error.code

        if isinstance(error, ValidationError):
            status_code = 400

        if not re.search(r"^[1-5]\d{2}$", str(status_code)):
            status_code = 500

        # populate error dict
        error_dict = dict(code=status_code)
        # TODO:: causing JSON serializer error for unknown types. Need to find a cleaner solution for this.
        # error_dict['extra_payload'] = error.args if hasattr(error, 'args') else None
        error_dict["extra_payload"] = dict()
        error_dict["message"] = error.message if hasattr(error, "message") else "Exception occurred."
        error_dict["developer_message"] = error.description if hasattr(error, "description") else str(error)
        error_dict["request_id"] = flask.g.request_id

    error_aggregate = app_core.infrastructure_service_registry.get_service('error_logger').log_api_error(
        response_code=status_code, request=request, message=error_dict['message'],
        developer_message=error_dict['developer_message'], stacktrace=traceback.format_exc(),
        error_code=error_dict.get('code'))
    app_core.get_telemetry_logger().logger.log_exception(
        response_code=status_code, message=error_dict['message'], developer_message=error_dict['developer_message'],
        stacktrace=traceback.format_exc(), error_code=error_dict.get('code'))
    if error_aggregate:
        error_dict['error_log_id'] = error_aggregate.error_log_id
    response = ApiResponseBuilder.build(errors=[error_dict], status_code=status_code)
    logger.exception(
        "URL: %s, Request/Response: request_id=%s, status=%s, error_log_id=%s",
        request.path,
        flask.g.request_id,
        response.status,
        error_dict.get("error_log_id"),
    )
    return response
