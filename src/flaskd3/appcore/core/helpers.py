import logging

from flask import request, session

from flaskd3.appcore.core.application_core import app_core
from flaskd3.appcore.core.request_context import get_organisation_id, set_organisation_id
from flaskd3.common.constants import ResourceOperation
from flaskd3.common.constants import SUPER_ORG_ID
from flaskd3.common.exceptions import (
    AuthenticationException,
    AuthorizationException,
)

logger = logging.getLogger(__name__)


def update_token_in_session():
    session["user_token"] = request.headers["Authorization"].split(" ")[1]


def reset_token_in_session():
    session["user_token"] = None


def authorize(user, resource_path, operation, scope=None, raise_exception=True):
    if not scope:
        scope = dict()
    if not app_core.get_acl_service("authz").is_operation_allowed(user.user_id, resource_path, operation, scope):
        if raise_exception:
            raise AuthorizationException(
                description="user does not have authorization to operate on the given resource",
                extra_payload=dict(
                    user_id=user.user_id,
                    organisation_id=get_organisation_id(),
                    resource_path=resource_path,
                    operation=str(operation),
                    scope=scope,
                ),
            )
        else:
            return False
    return True


def authorize_and_get_roles(user, resource_path, operation, scope=None, raise_exception=True):
    if not scope:
        scope = dict()
    roles = app_core.get_acl_service("authz").get_roles_if_operation_allowed(user.user_id, resource_path, operation,
                                                                             scope)
    if not roles and raise_exception:
        raise AuthorizationException(
            description="user does not have authorization to operate on the given resource",
            extra_payload=dict(
                user_id=user.user_id,
                organisation_id=get_organisation_id(),
                resource_path=resource_path,
                operation=str(operation),
                scope=scope,
            ),
        )
    return roles


def authorize_many(user, requests):
    return app_core.get_acl_service("authz").is_operation_allowed_bulk(user.user_id, requests)


def raise_authorization_exception(user, resource_path, operation, scope=None):
    raise AuthorizationException(
        description="user does not have authorization to operate on the given resource",
        extra_payload=dict(
            user_id=user.user_id,
            resource_path=resource_path,
            operation=str(operation),
            scope=scope,
        ),
    )


def filter_authorized(entities, user, resource_path, operation, scope_computer):
    filtered_entities = list()
    for entity in entities:
        if authorize(user, resource_path, operation, scope_computer(entity), False):
            filtered_entities.append(entity)
    return filtered_entities


def authenticate_session(allow_anonymous=False):
    token = session.get("user_token")
    user = None
    if token:
        user_service = app_core.get_acl_service("user")
        set_organisation_id(SUPER_ORG_ID)
        try:
            token = user_service.authenticate_session(token)
            user = user_service.get_user(token.user_id)
            if not user.is_active or not app_core.get_acl_service("authz").is_operation_allowed(
                    user.user_id, "/views", ResourceOperation.UPDATE):
                user = None
        except Exception as e:
            logger.exception("Authenticate session auth")
            user = None
    if not user and not allow_anonymous:
        raise AuthenticationException()
    return user


def queue_notification(application_id, template_id, recipients, channel, data, sender=None, extra_data=None):
    template_data = app_core.get_acl_service("templating").get_template_data(template_id, data)
    extra_data.update(template_data.get("extra_data"))
    return app_core.get_acl_service("notification").create_notification(
        application_id,
        recipients,
        template_data.get("header"),
        template_data.get("body"),
        channel,
        sender=sender,
        extra_data=extra_data,
    )


def call_with_db_commit(func, *args, **kwargs):
    db_service_provider = app_core.get_infra_service("db_service_provider")
    try:
        db_service_provider.init_transaction()
        r_val = func(*args, **kwargs)
        db_service_provider.commit()
        return r_val
    except Exception as e:
        db_service_provider.rollback()
        raise e
