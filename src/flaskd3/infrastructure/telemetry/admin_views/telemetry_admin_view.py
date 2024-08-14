from flaskd3.types.base_admin_view import BaseAdminView
from flaskd3.infrastructure.telemetry.repositories.models import TelemetryLogModel


class TelemetryAdminView(BaseAdminView):
    view_name = "Telemetry Logs"
    view_category = "Infrastructure"
    model_class = TelemetryLogModel
    can_create = False
    can_edit = False
    can_delete = False
    can_set_page_size = True
    can_view_details = True
    column_display_pk = True
    column_default_sort = ("started_at", True)

    column_exclude_list = ["deleted", "version", "modified_at"]
    column_searchable_list = [
        "request_id",
        "url"
    ]
