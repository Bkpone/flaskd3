from flaskd3.infrastructure.database.sqlalchemy.sql_base_aggregate_repository import (
    SQLABaseAggregateRepository,
)
from flaskd3.infrastructure.error_tracker.aggregates.api_error_log_aggregate import (
    APIErrorLogAggregate,
)
from flaskd3.infrastructure.error_tracker.repositories.models import APIErrorLogModel


class APIErrorLogRepository(SQLABaseAggregateRepository):
    name = "api_error_log_repository"
    aggregate_class = APIErrorLogAggregate
    entity_map = {APIErrorLogAggregate.__name__: APIErrorLogModel}
