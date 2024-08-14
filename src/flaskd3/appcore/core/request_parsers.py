# coding=utf-8
"""
Request Parsers
"""
import functools
import logging
from datetime import datetime
from enum import Enum

from flask import request
from marshmallow import Schema
from marshmallow.exceptions import ValidationError
from werkzeug.exceptions import UnsupportedMediaType

from flaskd3.appcore.core.request_context import set_currency
from flaskd3.appcore.schema.schema_manager import SchemaManager
from flaskd3.common.dtos.meta_dto import Meta
from flaskd3.common.exceptions import ApiValidationException
from flaskd3.common.money.constants import CurrencyType
from flaskd3.common.utils.file_utils import (
    is_valid_filename,
    validate_file_extensions,
)

logger = logging.getLogger(__name__)


class RequestTypes(Enum):
    JSON = "json"
    ARGS = "args"
    FORM = "form"
    MULTIPART = "multipart"

    @classmethod
    def type_from_content_type(cls, content_type):
        if "application/json" in content_type:
            return RequestTypes.JSON
        elif "application/x-www-form-urlencoded" in content_type:
            return RequestTypes.FORM
        elif "multipart/form-data" in content_type:
            return RequestTypes.MULTIPART
        else:
            return RequestTypes.ARGS


def with_slave():
    """
    with slave
    """

    def decorator(func):
        """
        decorator
        :param func:
        :return:
        """

        def wrapper(*args, **kwargs):
            """
            wrapper
            :param args:
            :param kwargs:
            :return:
            """
            setattr(request, "bind_name", "slave")
            return func(*args, **kwargs)

        return functools.update_wrapper(wrapper, func)

    return decorator


def parse_data_and_version(schema: Schema, request_types: RequestTypes, has_version: bool, many: bool, has_meta: bool = False):
    """
    @request_types is 'args' for GET APIs
                     'form' for POST APIs
                     'json' for POST APIs content-type application/json
    """

    def parse_data_and_version_inner(func):
        """
        validate_decorator
        :param func:
        :return:
        """

        def wrapper(*args, **kwargs):
            """
            wrapper
            :param args:
            :param kwargs:
            :return:
            """
            if isinstance(request_types, tuple):
                request_type = RequestTypes.type_from_content_type(request.content_type)
                if request_type not in request_types:
                    raise UnsupportedMediaType()
            else:
                request_type = request_types

            if request_type == RequestTypes.JSON and "application/json" not in request.content_type:
                raise UnsupportedMediaType()

            if request_type == RequestTypes.JSON and request.content_length == 0:
                data = dict()
            else:
                data = getattr(request, request_type.value)

            if request_type in [RequestTypes.ARGS, RequestTypes.FORM]:
                data = dict(data=data.to_dict())

            data["request_time"] = data.get("requestTime", datetime.now())

            meta = (
                data.get("meta")
                if not request_type in [RequestTypes.ARGS, RequestTypes.FORM]
                else dict(start=data["data"].get("start"), limit=data["data"].get("limit"), functionalCurrency=data["data"].get("functionalCurrency"))
            )
            if meta and has_meta:
                kwargs["meta"] = Meta(start=meta.get("start"), limit=meta.get("limit"))
            if meta:
                functional_currency = meta.get("functionalCurrency")
                if functional_currency:
                    functional_currency = CurrencyType(functional_currency)
                    set_currency(functional_currency)
            try:
                schema_obj = SchemaManager.get_schema_obj_from_class(schema)
                if not schema_obj:
                    schema_obj = schema(unknown="EXCLUDE")
                parsed_data = schema_obj.load(data.get("data", dict()), many=many)
            except ValidationError as e:
                logger.info("APIValidationError: %s", e.normalized_messages())
                raise ApiValidationException(extra_payload=e.normalized_messages())
            kwargs["parsed_request"] = parsed_data
            if has_version:
                if "resourceVersion" not in data or data.get("resourceVersion") is None:
                    raise ApiValidationException(extra_payload=dict(resource_version="This is a required field"))
                kwargs["resource_version"] = data.get("resourceVersion")

            return func(*args, **kwargs)

        return functools.update_wrapper(wrapper, func)

    return parse_data_and_version_inner


def schema_wrapper_and_version_parser(
    schema: Schema,
    many: bool = False,
    param_type: RequestTypes = RequestTypes.JSON,
    has_meta: bool = False,
):
    """

    Args:
        schema:
        many:
        param_type:

    Returns:

    """
    return parse_data_and_version(schema, param_type, has_version=True, many=many, has_meta=has_meta)


def schema_wrapper_parser(
    schema: Schema,
    many: bool = False,
    param_type: RequestTypes = RequestTypes.JSON,
    has_meta: bool = False,
):
    """

    Args:
        schema:
        many:
        param_type: json, form, args

    Returns:

    """
    return parse_data_and_version(schema, param_type, has_version=False, many=many, has_meta=has_meta)


def with_file():
    """
    decorator to enable access of uploaded file.
    :return:
    """

    def with_file_inner(func):
        """
        Inner function
        :param func:
        :return:
        """

        def wrapper(*args, **kwargs):
            request_type = RequestTypes.type_from_content_type(request.content_type)
            if request_type != RequestTypes.MULTIPART:
                raise UnsupportedMediaType()
            file = request.files.get("file")
            if not file:
                raise ApiValidationException(description="file data is missing")
            filename = file.filename
            if not filename:
                raise ApiValidationException(description="Empty file uploaded")
            if not is_valid_filename(filename):
                raise ApiValidationException(description="Invalid file name")
            kwargs["file"] = file
            return func(*args, **kwargs)

        return functools.update_wrapper(wrapper, func)

    return with_file_inner
