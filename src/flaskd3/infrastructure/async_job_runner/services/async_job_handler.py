import logging

from flaskd3.appcore.core.decorators import call_with_db_commit, handle_db_commits
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus

logger = logging.getLogger(__name__)


class AsyncJobHandler(object):
    def __init__(self, job_service):
        self.job_service = job_service

    @staticmethod
    def get_job_progress_handler(job_aggregate, job_service):
        return lambda response, should_append: call_with_db_commit(
            job_service.update_job,
            job_aggregate.update_status(AsyncJobStatus.PROCESSING, response, should_append),
        )

    @handle_db_commits
    def process_message(self, job_id):
        try:
            job_aggregate = self.job_service.get_job(job_id)
        except Exception as e:
            logger.exception("Error while executing job: %s" % job_id)
            return False
        logger.info("Started processing job id: %s" % job_aggregate.job_id)
        job_aggregate.update_status(AsyncJobStatus.PROCESSING, None)
        call_with_db_commit(self.job_service.update_job, job_aggregate)
        try:
            job_handler = self.job_service.get_handler(job_aggregate.job_name)
            kwargs = job_aggregate.extra_data.copy() if job_aggregate.extra_data else dict()
            if job_handler.update_progress:
                progress_handler = AsyncJobHandler.get_job_progress_handler(job_aggregate, self.job_service)
                kwargs["progress_handler"] = progress_handler
            if job_handler.need_job_data:
                kwargs["job_data"] = job_aggregate.get_job_data()
            response = job_handler.handler_func(**kwargs)
            state = AsyncJobStatus.FINISHED
        except Exception as e:
            logger.exception("Error while executing job: %s" % job_id)
            state = AsyncJobStatus.FAILED
            response = str(e)

        job_aggregate.update_status(state, response)
        self.job_service.update_job(job_aggregate)
        logger.info("Done processing job id: %s" % job_aggregate.job_id)
        return True
