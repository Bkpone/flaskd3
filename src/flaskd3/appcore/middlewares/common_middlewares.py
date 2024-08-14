# coding=utf-8
"""
Middlewares
"""
import logging
import time

import flask
from flask import redirect, url_for, session
from flask.globals import current_app

from flaskd3.appcore.core.helpers import authenticate_session, call_with_db_commit
from flaskd3.appcore.core.request_context import set_organisation_id, set_tenant_id
from flaskd3.appcore.core.application_core import app_core
from flaskd3.infrastructure.database.sqlalchemy.sql_db_service import SQLAlchemyDBService

logger = logging.getLogger(__name__)


def before_request():
    from flask import request, g

    g.request_start_time = time.time()
    add_request_id_header_to_request(request)
    extract_organisation_id_from_request(request)
    log_request(request)
    redirect_obj = authenticate_console(request)
    app_core.get_telemetry_logger().init_logger(request, g.request_id)
    if redirect_obj:
        return redirect_obj


def after_request(response):
    add_request_id_header_to_response(response)
    from flask import request, g

    enable_cors(response, request)
    add_auth_token_to_swagger_ui(request, response)
    if current_app.config["PROFILE"]:
        SQLAlchemyDBService.log_query_profile(
            "{} {}".format(request.method, request.url),
            current_app.config["PREF_OUTPUT"],
        )
    request_duration = time.time() - g.request_start_time
    logger.debug("Respond to request: {request_url} ({duration} seconds)".format(
        request_url=request.full_path, duration=round(request_duration, 2)))
    tel_logger = app_core.get_telemetry_logger()
    tel_logger.logger.set_response(response.json)
    call_with_db_commit(app_core.get_telemetry_logger().flush)
    return response


def log_request(request):
    """
    log request
    :return:
    """

    if not request.is_json:
        return
    # TODO change this back to debug after QA
    logger.debug(
        "Request received: request_id=%s, url=%s , headers=%s, payload=%s",
        flask.g.request_id,
        request.url,
        dict(request.headers),
        request.get_data(as_text=True),
    )


def add_request_id_header_to_request(request):
    """
    add X-Request-Id header to request if missing
    :return:
    """
    headers = request.headers
    request_id = headers.get("X-Request-Id")
    if not request_id:
        request_id = _generate_request_id()
    import flask

    flask.g.request_id = request_id
    # Initialise domain events array
    flask.g.events = list()


def add_request_id_header_to_response(response):
    """
    add X-Request-Id header to response
    :param response:
    :return:
    """
    import flask

    response.headers["X-Request-Id"] = flask.g.request_id
    return response


def extract_organisation_id_from_request(request):
    """
    Extract organisation id from the request
    :param request:
    :return:
    """
    set_organisation_id(request.headers.get("X-Org-Id"))
    set_tenant_id(request.headers.get("X-Tenant-Id"))


def enable_cors(response, request):
    response.headers["Access-Control-Allow-Origin"] = "*"
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Methods"] = "DELETE, GET, POST, PUT, PATCH"
        headers = request.headers.get("Access-Control-Request-Headers")
        if headers:
            response.headers["Access-Control-Allow-Headers"] = headers
    return response


def _generate_request_id():
    import uuid

    return uuid.uuid4().hex


def add_auth_token_to_swagger_ui(request, response):
    if "/apispec_1.json" in request.url:
        response.headers["jwt-token"] = session.get("user_token")


def authenticate_console(request):
    if "/view" in request.url:
        if authenticate_session(allow_anonymous=True) is None:
            return redirect(url_for("ConsoleService.login", next=request.url))
    return None
