import logging

from flaskd3.appcore.core.decorators import handle_db_commits
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus

logger = logging.getLogger(__name__)


class RecurringJobPublisher(object):
    def __init__(self, recurring_job_repository, job_service):
        self.recurring_job_repository = recurring_job_repository
        self.job_service = job_service

    @handle_db_commits
    def publish_jobs(self, run_datetime):
        recurring_job_aggregates = self.recurring_job_repository.get_jobs(run_datetime=run_datetime)
        fail_count = 0
        if not recurring_job_aggregates:
            return 0, fail_count
        for recurring_job_aggregate in recurring_job_aggregates:
            try:
                next_run_datetime = recurring_job_aggregate.next_run_datetime if recurring_job_aggregate.schedule_pending else run_datetime
                logger.debug(
                    "Scheduling job with id: %s at %s",
                    recurring_job_aggregate.recurring_job_id,
                    next_run_datetime,
                )
                job_aggregate = self.job_service.write(
                    recurring_job_aggregate.job_name,
                    recurring_job_aggregate.extra_data,
                    next_run_datetime,
                )
                recurring_job_aggregate.log_run(job_aggregate)
            except Exception as e:
                logger.exception(
                    "Error while scheduling job with id: %s",
                    recurring_job_aggregate.recurring_job_id,
                )
                recurring_job_aggregate.status = AsyncJobStatus.FAILED
                fail_count += 1

        self.recurring_job_repository.update_all(recurring_job_aggregates)
        return len(recurring_job_aggregates), fail_count
