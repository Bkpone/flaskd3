import logging

from flaskd3.appcore.core.decorators import handle_db_commits
from flaskd3.infrastructure.domain_events.constants import DomainEventStatus

logger = logging.getLogger(__name__)


class DomainEventPublisher:
    def __init__(self, event_repository, publisher):
        self.event_repository = event_repository
        self.publisher = publisher

    @handle_db_commits
    def publish_latest(self, domain):
        event_aggregates = self.event_repository.get_unpublished_events(domain)
        fail_count = 0
        for event_aggregate in event_aggregates:
            try:
                self.publisher.publish(event_aggregate)
                event_aggregate.status = DomainEventStatus.PUBLISHED
            except Exception as e:
                fail_count += 1
                logger.exception(
                    "Error while publishing integration event with id: %s",
                    event_aggregate.event_id,
                )
                event_aggregate.status = DomainEventStatus.FAILED
        self.event_repository.update_all(event_aggregates)
        return len(event_aggregates), fail_count
