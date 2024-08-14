import logging

from flaskd3.appcore.core.decorators import handle_db_commits
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus

logger = logging.getLogger(__name__)


class JobPublisher(object):
    def __init__(self, job_repository, publisher):
        self.job_repository = job_repository
        self.publisher = publisher

    @handle_db_commits
    def publish_jobs(self, run_datetime):
        job_aggregates = self.job_repository.get_jobs(run_datetime=run_datetime)
        fail_count = 0
        if not job_aggregates:
            return 0, fail_count
        for job_aggregate in job_aggregates:
            try:
                logger.debug("Scheduling job with id: %s", job_aggregate.job_id)
                self.publisher.publish(job_aggregate)
                job_aggregate.status = AsyncJobStatus.ENQUEUE
            except Exception as e:
                logger.exception("Error while scheduling job with id: %s", job_aggregate.job_id)
                job_aggregate.status = AsyncJobStatus.FAILED
                fail_count += 1
                job_aggregate.response = str(e)

        self.job_repository.update_all(job_aggregates)
        return len(job_aggregates), fail_count
