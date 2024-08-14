from flaskd3.types.base_admin_view import BaseAdminView
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus
from flaskd3.infrastructure.async_job_runner.repositories.models import RecurringJobModel


class RecurringJobAdminView(BaseAdminView):
    view_name = "Recurring Jobs"
    view_category = "Infrastructure"
    model_class = RecurringJobModel
    can_create = True
    can_edit = True
    can_delete = False
    can_set_page_size = True
    can_view_details = True
    column_display_pk = True
    column_default_sort = ("created_at", True)

    column_exclude_list = ["deleted"]
    column_searchable_list = ["recurring_job_id", "extra_data"]
    column_filters = ["job_name", "status"]

    column_choices = {"status": AsyncJobStatus.all_values()}
