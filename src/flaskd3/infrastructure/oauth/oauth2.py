import json

from authlib.flask.oauth2 import AuthorizationServer, ResourceProtector
from authlib.flask.oauth2.sqla import (
    create_query_client_func,
    create_save_token_func,
    create_revocation_endpoint,
    create_bearer_token_validator,
)
from authlib.specs.rfc6749 import grants, OAuth2Error
from werkzeug.security import gen_salt

from flaskd3.common.exceptions import (
    ValidationException,
    AuthenticationException,
    InvalidStateException,
)
from .models import db
from flaskd3.infrastructure.oauth.models import (
    OAuth2ClientModel,
    OAuth2AuthorizationCodeModel,
    OAuth2TokenModel,
)

DEFAULT_GLOBAL_SCOPE = "global"


class AuthCallback(object):
    get_user_by_name = None
    get_user_by_id = None
    authenticate_user = None
    authenticate_otp = None

    def __init__(self, get_user_by_name, get_user_by_id, authenticate_user, authenticate_otp):
        self.get_user_by_name = get_user_by_name
        self.get_user_by_id = get_user_by_id
        self.authenticate_user = authenticate_user
        self.authenticate_otp = authenticate_otp


class SessionTokenProtector:
    def register_token_validator(self, validator):
        self.validator = validator

    def validate_request(self, token_string, scope, request, scope_operator="AND"):
        return self.validator(token_string, scope, request, scope_operator)


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def create_authorization_code(self, client, user, request):
        code = gen_salt(48)
        item = OAuth2AuthorizationCodeModel(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=DEFAULT_GLOBAL_SCOPE,
            user_id=user.user_id,
        )
        db.session.add(item)
        db.session.commit()
        return code

    def parse_authorization_code(self, code, client):
        item = OAuth2AuthorizationCodeModel.query.filter_by(code=code, client_id=client.client_id).first()
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(self, authorization_code):
        return auth_callback.get_user_by_id(authorization_code.user_id)


class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        user = auth_callback.get_user_by_name(username)
        if auth_callback.authenticate_user(user, password):
            return user


class OTPGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    GRANT_TYPE = "otp"

    def authenticate_user(self, username, otp_hash):
        if auth_callback.authenticate_otp(username, otp_hash):
            user = auth_callback.get_user_by_name(username)
            return user


class RefreshTokenGrant(grants.RefreshTokenGrant):
    def authenticate_refresh_token(self, refresh_token):
        item = OAuth2TokenModel.query.filter_by(refresh_token=refresh_token).first()
        if item and not item.is_refresh_token_expired():
            return item

    def authenticate_user(self, credential):
        return auth_callback.get_user_by_id(credential.user_id)


query_client = create_query_client_func(db.session, OAuth2ClientModel)
save_token = create_save_token_func(db.session, OAuth2TokenModel)
authorization = AuthorizationServer(
    query_client=query_client,
    save_token=save_token,
)
require_oauth = ResourceProtector()
session_oauth = SessionTokenProtector()
auth_callback = None


def config_oauth(app):
    authorization.init_app(app)

    # support all grants
    authorization.register_grant(grants.ImplicitGrant)
    authorization.register_grant(grants.ClientCredentialsGrant)
    authorization.register_grant(AuthorizationCodeGrant)
    authorization.register_grant(PasswordGrant)
    authorization.register_grant(RefreshTokenGrant)
    authorization.register_grant(OTPGrant)

    # support revocation
    revocation_cls = create_revocation_endpoint(db.session, OAuth2TokenModel)
    authorization.register_endpoint(revocation_cls)

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2TokenModel)
    require_oauth.register_token_validator(bearer_cls())
    session_oauth.register_token_validator(bearer_cls())


def validate_session_token(scope, token, request):
    try:
        return session_oauth.validate_request(token_string=token, scope=scope, request=request)
    except OAuth2Error as error:
        status = error.status_code
        body = json.dumps(dict(error.get_body()))
        if status in [401, 403]:
            raise AuthenticationException(extra_payload=body)
        elif status == 400:
            raise ValidationException(extra_payload=body)
        else:
            raise InvalidStateException(extra_payload=body)


def validate_token(scope, request):
    try:
        return require_oauth.validate_request(scope=scope, request=request)
    except OAuth2Error as error:
        status = error.status_code
        body = json.dumps(dict(error.get_body()))
        if status in [401, 403]:
            raise AuthenticationException(extra_payload=body)
        elif status == 400:
            raise ValidationException(extra_payload=body)
        else:
            raise InvalidStateException(extra_payload=body)
