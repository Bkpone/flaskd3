import logging

from flaskd3.infrastructure.domain_events.constants import DomainEventStatus
from flaskd3.infrastructure.domain_events.factories.domain_event_factory import (
    DomainEventFactory,
)


logger = logging.getLogger(__name__)


class DomainEventProcessor(object):
    def __init__(self, handler):
        self.handler = handler

    def process_domain_event(self, consumed_domain_event_aggregate):
        try:
            updates = DomainEventFactory.parse_events(consumed_domain_event_aggregate.raw_updates)
            consumed_domain_event_aggregate.updates.update(updates)
            event_processed, details = self.handler.process_domain_event(consumed_domain_event_aggregate)
            if event_processed:
                consumed_domain_event_aggregate.status = DomainEventStatus.PROCESSED
            else:
                consumed_domain_event_aggregate.status = DomainEventStatus.IGNORED
            consumed_domain_event_aggregate.details = str(details)
        except Exception as e:
            logger.exception("Failed processing event_id: {}".format(consumed_domain_event_aggregate.event_id))
            consumed_domain_event_aggregate.status = DomainEventStatus.FAILED
            consumed_domain_event_aggregate.details = str(e)
        return consumed_domain_event_aggregate
