from flaskd3.infrastructure.async_job_runner.aggregates.job_aggregate import JobAggregate
from flaskd3.infrastructure.async_job_runner.constants import AsyncJobStatus
from flaskd3.infrastructure.async_job_runner.repositories.models import JobModel
from flaskd3.infrastructure.database.sqlalchemy.sql_base_aggregate_repository import (
    SQLABaseAggregateRepository,
)


class JobRepository(SQLABaseAggregateRepository):

    name = "job_repository"

    aggregate_class = JobAggregate

    entity_map = {JobAggregate.__name__: JobModel}

    def get_jobs(self, run_datetime, for_update=True):
        queries = [
            JobModel.status == AsyncJobStatus.CREATED.value,
            JobModel.run_time <= run_datetime,
        ]
        return self.load_multiple_queries(for_update, False, JobModel.created_at.asc(), False, None, *queries)
