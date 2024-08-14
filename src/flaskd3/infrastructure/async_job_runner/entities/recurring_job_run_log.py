from datetime import datetime
from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.type_info import TypeInfo
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus


class RecurringJobRunLog(BaseEntity):

    is_multi_tenant = True

    recurring_job_run_log_id = TypeInfo(str, primary_key=True)
    job_id = TypeInfo(str)
    status = TypeInfo(AsyncJobStatus)
    run_datetime = TypeInfo(datetime)
