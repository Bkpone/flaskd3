from flaskd3.infrastructure.database.sqlalchemy.sql_base_aggregate_repository import (
    SQLABaseAggregateRepository,
)
from flaskd3.infrastructure.telemetry.aggregates.telemetry_log_aggregate import (
    TelemetryLogAggregate,
)
from flaskd3.infrastructure.telemetry.repositories.models import TelemetryLogModel


class TelemetryRepository(SQLABaseAggregateRepository):
    name = "telemetry_log_repository"
    aggregate_class = TelemetryLogAggregate
    entity_map = {TelemetryLogAggregate.__name__: TelemetryLogModel}
