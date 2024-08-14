from flaskd3.types.base_admin_view import BaseAdminView
from flaskd3.infrastructure.error_tracker.repositories.models import APIErrorLogModel


class APIErrorLogAdminView(BaseAdminView):
    view_name = "API Error Logs"
    view_category = "Infrastructure"
    model_class = APIErrorLogModel
    can_create = False
    can_edit = False
    can_delete = False
    can_set_page_size = True
    can_view_details = True
    column_display_pk = True
    column_default_sort = ("created_at", True)

    column_exclude_list = ["deleted", "version", "modified_at", "stacktrace", "payload"]
    column_searchable_list = [
        "message",
        "developer_message",
        "stacktrace",
        "error_log_id",
    ]
    column_filters = ["response_code", "error_code"]

    column_formatters = dict(stacktrace=lambda v, c, m, p: m.stacktrace[:150] + ".." if m.stacktrace and len(m.stacktrace) > 150 else m.stacktrace)
    column_formatters_detail = dict()
