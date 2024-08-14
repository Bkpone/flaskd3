from datetime import datetime

from flaskd3.common.utils.dateutils import current_datetime
from flaskd3.common.utils.id_generator_utils import generate_id_with_prefix
from flaskd3.infrastructure.async_job_runner.aggregates.job_aggregate import JobAggregate
from flaskd3.infrastructure.async_job_runner.aggregates.recurring_job_aggregate import (
    RecurringJobAggregate,
)
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus


class JobFactory:
    @staticmethod
    def create_job(job_name, extra_data, run_time):
        job_aggregate = JobAggregate(
            job_id=generate_id_with_prefix("job"),
            job_name=job_name,
            extra_data=extra_data,
            run_time=run_time,
            status=AsyncJobStatus.CREATED,
            response=None,
            created_at=current_datetime(),
            modified_at=current_datetime(),
        )
        return job_aggregate

    @staticmethod
    def create_recurring_job(name, job_name, extra_data, schedule, is_active=True, schedule_pending=False):
        recurring_job_aggregate = RecurringJobAggregate(
            recurring_job_id=generate_id_with_prefix("rjob"),
            job_name=job_name,
            name=name,
            extra_data=extra_data,
            last_run_datetime=None,
            status=AsyncJobStatus.CREATED,
            schedule_pending=schedule_pending,
            next_run_datetime=None,
            schedule=schedule,
            is_active=is_active,
            created_at=current_datetime(),
            modified_at=current_datetime(),
            run_log=None,
        )
        recurring_job_aggregate.update_next_run_datetime(current_datetime())
        return recurring_job_aggregate
