from flaskd3.infrastructure.database.sqlalchemy.db_adapter import DBAdapter
from flaskd3.infrastructure.database.sqlalchemy.sql_base_aggregate_repository import (
    SQLABaseAggregateRepository,
)
from flaskd3.infrastructure.domain_events.aggregates.domain_event_aggregate import (
    DomainEventAggregate,
)
from flaskd3.infrastructure.domain_events.constants import DomainEventStatus
from flaskd3.infrastructure.domain_events.repositories.models import DomainEventModel


class DomainEventRepository(SQLABaseAggregateRepository):

    name = "domain_event_repository"

    aggregate_class = DomainEventAggregate

    entity_map = {DomainEventAggregate.__name__: DomainEventModel}

    def get_unpublished_events(self, domain=None):
        queries = [DomainEventModel.status.in_((DomainEventStatus.CREATED.value, DomainEventStatus.FAILED.value))]
        if domain:
            queries.append(DomainEventModel.domain == domain)
        integration_event_models = (
            self.session().query(DomainEventModel).filter(*queries).order_by(DomainEventModel.generated_at.asc()).with_for_update(nowait=False)
        )
        if not integration_event_models:
            return []
        aggregates = DBAdapter(self.entity_map, self).load_aggregates_by_models(self.aggregate_class, integration_event_models, False)
        return aggregates
