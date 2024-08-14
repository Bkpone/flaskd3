# coding=utf-8
"""
Exceptions
"""
import uuid

from flaskd3.types.base_enum import BaseEnum


class FDError(BaseEnum):
    @property
    def error_code(self):
        return self.values[0]

    @property
    def message(self):
        return self.values[1]


class DCException(Exception):
    error_code = "0001"
    message = "Something went wrong. Please contact escalations team"

    def __init__(self, description=None, extra_payload=None, message=None):
        self.description = description
        self.extra_payload = extra_payload
        self.error_id = uuid.uuid4()
        if message is not None:
            self.message = message

    def __str__(self):
        return "exception(%s): error_code=%s message=%s description=%s extra payload:%s" % (
            self.error_id,
            self.error_code,
            self.message,
            self.description,
            self.extra_payload

        )

    def with_description(self, description):
        self.description = description
        return self

    @property
    def code(self):
        return "0401" + self.error_code


class ValidationException(DCException):
    error_code = "0002"
    message = "Validation Exception"

    def __init__(self, error=None, description=None, message=None, extra_payload=None):
        if error and isinstance(error, FDError):
            self.error_code = error.error_code
            self.message = error.message
        else:
            if message:
                self.message = message
            if isinstance(error, str) and not description:
                description = error
        super(ValidationException, self).__init__(description=description, extra_payload=extra_payload)


class DatabaseError(DCException):
    error_code = "0003"
    message = "Something went wrong with the database"


class ResourceNotFound(DCException):
    error_code = "0004"
    message = "{} Not found."

    def __init__(self, resource_name, description=None, extra_payload=None):
        super(ResourceNotFound, self).__init__(
            message=self.message.format(resource_name),
            description=description,
            extra_payload=extra_payload,
        )


class DuplicateResourceFound(DCException):
    error_code = "0005"
    message = "Duplicate {} found"

    def __init__(self, resource_name, resource_id, description=None):
        super(DuplicateResourceFound, self).__init__(
            message=self.message.format(resource_name),
            description=description,
            extra_payload=dict(resource_id=resource_id),
        )


class OutdatedVersion(DCException):
    error_code = "0005"

    def __init__(self, class_name, old_version, current_version):
        self.message = "Outdated version. Refresh and please try again."
        description = "Load failed for {}:{} current version: {}.".format(class_name, old_version, current_version)
        super(OutdatedVersion, self).__init__(description=description, extra_payload="")


class ApiValidationException(DCException):
    error_code = "0006"
    message = "Request Invalid"


class AggregateNotFound(ResourceNotFound):
    error_code = "0007"

    def __init__(self, resource_name, resource_id=None, extra_payload=""):
        description = "Aggregate: {} with id: {} missing.".format(resource_name, resource_id)
        super(AggregateNotFound, self).__init__(resource_name, description=description, extra_payload=extra_payload)


class AuthorizationException(DCException):
    error_code = "0008"
    message = "Unauthorized Operation"

    def __init__(self, description=None, extra_payload=None):
        super(AuthorizationException, self).__init__(description=description, extra_payload=extra_payload)


class DownstreamSystemFailure(DCException):
    error_code = "0009"
    message = "Downstream system failed."

    def __init__(self, message=None, description=None, extra_payload=None):
        self.message = message
        super(DownstreamSystemFailure, self).__init__(description=description, extra_payload=extra_payload)


class AuthenticationException(DCException):
    error_code = "0010"
    message = "Unable to authenticate user."

    def __init__(self, description=None, extra_payload=None):
        super(AuthenticationException, self).__init__(description=description, extra_payload=extra_payload)


class ConfigurationError(DCException):
    error_code = "0020"
    message = "Configuration error in flaskd3."

    def __init__(self, description=None, extra_payload=None):
        super(ConfigurationError, self).__init__(description=description, extra_payload=extra_payload)


class RedisError(ValidationException):
    error_code = "0011"
    message = "Unable to store in redis database"

    def __init__(self, description=None, extra_payload=None):
        super(RedisError, self).__init__(description=description, extra_payload=extra_payload)


class InvalidStateException(DCException):
    error_code = "0016"
    message = "Something went wrong. Please contact Escalations team"

    def __init__(self, error=None, description=None, message=None, extra_payload=None):
        if error:
            self.error_code = error.error_code
            self.message = error.message
        else:
            self.error_code = self.error_code
            self.message = message if message else self.message
        super().__init__(description=description, extra_payload=extra_payload)


def get_http_status_code_from_exception(exception: DCException) -> int:
    if isinstance(exception, AuthorizationException):
        return 403

    if isinstance(exception, ApiValidationException):
        return 400

    if isinstance(exception, InvalidStateException):
        return 500

    if isinstance(exception, AuthenticationException):
        return 401

    return 400
