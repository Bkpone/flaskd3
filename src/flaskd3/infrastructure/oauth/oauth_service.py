from authlib.specs.rfc6749 import OAuth2Error
from flask import render_template, request
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.security import gen_salt

from flaskd3.infrastructure.oauth import oauth2
from flaskd3.infrastructure.oauth.oauth2 import (
    AuthCallback,
    OAuth2ClientModel,
    db,
    DEFAULT_GLOBAL_SCOPE,
)


class OAuthService(object):
    def initialize(self, get_user_by_name, get_user_by_id, authenticate_user, authenticate_otp):
        oauth2.auth_callback = AuthCallback(get_user_by_name, get_user_by_id, authenticate_user, authenticate_otp)

    def register_client(self, new_client_data, user):
        if "grant_types" in new_client_data:
            grant_types = new_client_data.pop("grant_types")
        client = OAuth2ClientModel(**new_client_data)
        if user:
            client.user_id = user.user_id
        client.grant_types = grant_types
        client.client_id = gen_salt(24)
        client.scope = DEFAULT_GLOBAL_SCOPE
        if client.token_endpoint_auth_method == "none":
            client.client_secret = ""
        else:
            client.client_secret = gen_salt(48)
        db.session.add(client)
        db.session.commit()
        return client

    def validate_consent(self):
        try:
            grant = oauth2.authorization.validate_consent_request()
        except OAuth2Error as error:
            return error.error
        return render_template("authorize.html", grant=grant)

    def authorize(self, user):
        if request.form["confirm"]:
            grant_user = user
        else:
            grant_user = None
        data = oauth2.authorization.create_authorization_response(grant_user=grant_user)
        return data

    def issue_token(self, grant_type, username, password, code=None, redirect_uri=None):
        param_list = [
            ("scope", DEFAULT_GLOBAL_SCOPE),
            ("grant_type", grant_type),
            ("username", username),
            ("password", password),
        ]

        if code:
            param_list.append(("code", code))

        if redirect_uri:
            param_list.append(("redirect_uri", redirect_uri))

        request.form = ImmutableMultiDict(param_list)
        token = oauth2.authorization.create_token_response(request=request)
        return token

    def configure(self, app):
        oauth2.config_oauth(app)

    def require_oauth(self):
        return oauth2.validate_token(scope=DEFAULT_GLOBAL_SCOPE, request=request)

    def validate_session(self, token):
        return oauth2.validate_session_token(scope=DEFAULT_GLOBAL_SCOPE, token=token, request=request)
