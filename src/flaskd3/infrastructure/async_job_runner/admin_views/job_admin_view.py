from flaskd3.types.base_admin_view import BaseAdminView
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus
from flaskd3.infrastructure.async_job_runner.repositories.models import JobModel


class JobAdminView(BaseAdminView):
    view_name = "Async Jobs"
    view_category = "Infrastructure"
    model_class = JobModel
    can_create = True
    can_edit = False
    can_delete = False
    can_set_page_size = True
    can_view_details = True
    column_display_pk = True
    column_default_sort = ("created_at", True)

    column_exclude_list = ["deleted"]
    column_searchable_list = ["job_id", "response", "extra_data"]
    column_editable_list = ["status"]
    column_filters = ["job_name", "status"]
    column_formatters = dict(response=lambda v, c, m, p: m.response[:150] + ".." if m.response and len(m.response) > 150 else m.response)

    column_formatters_detail = dict()

    column_choices = {"status": AsyncJobStatus.all_values()}
