from flask.helpers import url_for
from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import redirect
from flask import request

from flaskd3.appcore.core.application_core import app_core


class BaseModelView(ModelView):
    def is_accessible(self):
        user_service = app_core.get_acl_service("user")
        token = user_service.authenticate()
        return token is not None

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for("login", next=request.url))
