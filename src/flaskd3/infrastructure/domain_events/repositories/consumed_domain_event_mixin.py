from flaskd3.infrastructure.database.sqlalchemy.db_adapter import DBAdapter
from flaskd3.infrastructure.domain_events.constants import DomainEventStatus


class ConsumedDomainEventRepositoryMixin(object):
    def get_retry_events(self, count):
        model = self.entity_map[self.aggregate_class.__name__]
        queries = [model.status == DomainEventStatus.RETRY_PENDING.value]

        integration_event_models = (
            self.session().query(model).filter(*queries).order_by(model.generated_at.asc()).with_for_update(nowait=False).limit(count)
        )
        if not integration_event_models:
            return []
        aggregates = DBAdapter(self.entity_map, self).load_aggregates_by_models(self.aggregate_class, integration_event_models)
        for aggregate in aggregates:
            aggregate.status = DomainEventStatus.RETRYING
        return aggregates
