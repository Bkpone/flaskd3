import logging

from flaskd3.appcore.core.decorators import call_with_db_commit, handle_db_commits
from flaskd3.infrastructure.domain_events.constants import DomainEventStatus
from flaskd3.infrastructure.domain_events.factories.domain_event_factory import (
    DomainEventFactory,
)
from flaskd3.infrastructure.messaging.base_message_processor import BaseMessageProcessor
from flaskd3.common.exceptions import AggregateNotFound

logger = logging.getLogger(__name__)


class DomainEventConsumer(BaseMessageProcessor):
    def __init__(self, event_repository, domain_event_processor):
        self.event_repository = event_repository
        self.domain_event_processor = domain_event_processor

    @handle_db_commits
    def process_message(self, message_data):
        try:
            consumed_domain_event_aggregate = self.event_repository.load(message_data.get("eventId"))
        except AggregateNotFound:
            consumed_domain_event_aggregate = None

        new_event = False
        if not consumed_domain_event_aggregate:
            try:
                consumed_domain_event_aggregate = DomainEventFactory.create_domain_event_from_data(message_data)
                new_event = True
            except Exception as e:
                logger.exception("Domain Event Create failed")
                return False

        if consumed_domain_event_aggregate.status not in (
            DomainEventStatus.CREATED,
            DomainEventStatus.RETRY_PENDING,
        ):
            logger.info(
                "Event: {} already processed with status: {}".format(
                    consumed_domain_event_aggregate.event_id,
                    consumed_domain_event_aggregate.status.value,
                )
            )
            return True
        consumed_domain_event_aggregate = self.domain_event_processor.process_domain_event(consumed_domain_event_aggregate)
        if new_event:
            self.event_repository.save(consumed_domain_event_aggregate)
        else:
            self.event_repository.update(consumed_domain_event_aggregate)
        return True

    def _process_single_event(self, consumed_domain_event_aggregate):
        consumed_domain_event_aggregate = self.domain_event_processor.process_domain_event(consumed_domain_event_aggregate)
        self.event_repository.update(consumed_domain_event_aggregate)

    def _fetch_failed_events(self, count):
        consumed_domain_event_aggregates = self.event_repository.get_retry_events(count)
        self.event_repository.update_all(consumed_domain_event_aggregates)
        return consumed_domain_event_aggregates

    def retry_failed_messages(self):
        consumed_domain_event_aggregates = call_with_db_commit(self._fetch_failed_events, 1)
        processed = 0
        still_failed = 0
        for consumed_domain_event_aggregate in consumed_domain_event_aggregates:
            call_with_db_commit(self._process_single_event, consumed_domain_event_aggregate)
            if consumed_domain_event_aggregate.status == DomainEventStatus.FAILED:
                still_failed += 1
            else:
                processed += 1
        return processed, still_failed
