from flask import redirect, url_for, request
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.filters import BaseSQLAFilter

from flaskd3.common.utils.dateutils import month_datetime_range
from flaskd3.appcore.core.helpers import authenticate_session


class BaseAdminView(ModelView):
    view_name = None
    view_category = "Others"

    def is_accessible(self):
        return authenticate_session(allow_anonymous=True) is not None

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("ConsoleService.login", next=request.url))


class FilterInMonth(BaseSQLAFilter):
    def apply(self, query, value, alias=None):
        month, year = value.split("/")
        start_datetime, end_datetime = month_datetime_range(int(month), int(year))
        return query.filter(self.column >= start_datetime, self.column < end_datetime)

    def validate(self, value):
        return len(value.split("/")) == 2

    def operation(self):
        return "in month"
