import logging
from functools import wraps

from authlib.specs.rfc6749 import UnauthorizedClientError

from flaskd3.appcore.core.application_core import app_core
from flaskd3.appcore.core.request_context import get_organisation_id, set_current_user
from flaskd3.common.exceptions import (
    AuthenticationException,
    AuthorizationException,
)

logger = logging.getLogger(__name__)


def handle_db_commits(func):
    """
    Handle DB commits
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Wrapper
        :param args:
        :param kwargs:
        :return:
        """
        db_service_provider = app_core.get_infra_service("db_service_provider")
        domain_event_service = app_core.get_infra_service("domain_event_service")
        try:
            db_service_provider.init_transaction()
            r_val = func(*args, **kwargs)
            domain_event_service.commit_all()
            db_service_provider.commit()
            return r_val
        except Exception as e:
            db_service_provider.rollback()
            raise e

    return wrapper


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


def authenticate(get_user=False, allow_anonymous=False):
    def authenticate_inner(func):
        """
        require oauth
        :param func:
        :return:
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper
            :param args:
            :param kwargs:
            :return:
            """
            user_service = app_core.get_acl_service("user")
            try:
                token = user_service.authenticate()
            except AuthenticationException:
                token = None
            if not token and not allow_anonymous:
                raise AuthenticationException()
            user = user_service.get_user(token.user_id) if token else None
            if user and not user.is_active:
                raise AuthenticationException()
            organisation_id = get_organisation_id()
            if organisation_id is not None:
                if user:
                    is_member = app_core.get_acl_service("authz").is_member_of_organisation(user.user_id, organisation_id)
                    if not is_member:
                        raise AuthorizationException(description="User {} is not a member of {}".format(user.user_id, organisation_id))
                else:
                    if not allow_anonymous:
                        raise AuthenticationException()
            if get_user:
                kwargs["user"] = user
            set_current_user(user)
            if user:
                app_core.get_telemetry_logger().logger.set_user_id(user.user_id)
            r_val = func(*args, **kwargs)
            return r_val

        return wrapper

    return authenticate_inner


def get_user_by_token():
    def auth(func):
        """
        require oauth
        :param func:
        :return:
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper
            :param args:
            :param kwargs:
            :return:
            """
            try:
                user_application_service = app_core.get_acl_service("user")
                token = user_application_service.get()
                if token:
                    r_val = func(*args, **kwargs)
                else:
                    return UnauthorizedClientError
                return r_val
            except Exception as e:
                raise e

        return wrapper

    return auth
