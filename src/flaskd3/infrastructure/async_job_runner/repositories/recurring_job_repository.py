from flaskd3.infrastructure.async_job_runner.aggregates.recurring_job_aggregate import (
    RecurringJobAggregate,
)
from flaskd3.infrastructure.async_job_runner.entities.recurring_job_run_log import (
    RecurringJobRunLog,
)
from flaskd3.infrastructure.async_job_runner.repositories.models import (
    RecurringJobModel,
    RecurringJobRunLogModel,
)
from flaskd3.infrastructure.database.sqlalchemy.sql_base_aggregate_repository import (
    SQLABaseAggregateRepository,
)
from flaskd3.common.utils.dateutils import datetime_to_utc


class RecurringJobRepository(SQLABaseAggregateRepository):

    name = "recurring_job_repository"

    aggregate_class = RecurringJobAggregate

    entity_map = {
        RecurringJobAggregate.__name__: RecurringJobModel,
        RecurringJobRunLog.__name__: RecurringJobRunLogModel,
    }

    def get_jobs(self, run_datetime, for_update=True):
        queries = [
            RecurringJobModel.next_run_datetime <= datetime_to_utc(run_datetime),
            RecurringJobModel.is_active == True,
        ]
        return self.load_multiple_queries(for_update, True, RecurringJobModel.created_at.asc(), False, None, *queries)
