import time

from authlib.flask.oauth2.sqla import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)

from flaskd3.infrastructure.database.sqlalchemy.orm_base import db


class OAuth2ClientModel(db.Model, OAuth2ClientMixin):
    __tablename__ = "oauth2_client"

    id = db.Column(db.Integer, primary_key=True)
    client_organization_id = db.Column(db.String(64))
    user_id = db.Column(db.String(64))


class OAuth2AuthorizationCodeModel(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = "oauth2_code"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)


class OAuth2TokenModel(db.Model, OAuth2TokenMixin):
    __tablename__ = "oauth2_token"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64))

    def is_refresh_token_expired(self):
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at < time.time()
