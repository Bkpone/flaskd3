from datetime import datetime

from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.type_info import TypeInfo
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus
from flaskd3.infrastructure.async_job_runner.entities.recurring_job_run_log import (
    RecurringJobRunLog,
)
from flaskd3.infrastructure.async_job_runner.value_objects import RecurringJobSchedule


class RecurringJobAggregate(BaseEntity):

    is_multi_tenant = True

    recurring_job_id = TypeInfo(str, primary_key=True)
    extra_data = TypeInfo(dict)
    name = TypeInfo(str)
    job_name = TypeInfo(str, allow_none=True)
    last_run_datetime = TypeInfo(datetime, allow_none=True)
    next_run_datetime = TypeInfo(datetime, allow_none=True)
    status = TypeInfo(AsyncJobStatus)
    is_active = TypeInfo(bool)
    schedule = TypeInfo(RecurringJobSchedule)
    run_log = TypeInfo(RecurringJobRunLog, many=True)
    schedule_pending = TypeInfo(bool)
    created_at = TypeInfo(datetime)
    modified_at = TypeInfo(datetime)

    def log_run(self, job_aggregate):
        self.status = AsyncJobStatus.ENQUEUE
        self.last_run_datetime = job_aggregate.run_time
        self.update_next_run_datetime(job_aggregate.run_time)
        self.run_log.add(
            RecurringJobRunLog(
                recurring_job_run_log_id=self.run_log.get_next_id(),
                status=AsyncJobStatus.CREATED,
                job_id=job_aggregate.job_id,
                run_datetime=job_aggregate.run_time,
            )
        )

    def update_next_run_datetime(self, last_run_datetime):
        self.next_run_datetime = self.schedule.next_run_datetime(last_run_datetime)
