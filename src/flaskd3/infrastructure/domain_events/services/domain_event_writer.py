from flaskd3.infrastructure.domain_events.factories.domain_event_factory import (
    DomainEventFactory,
)
from flaskd3.common.constants import UpdateType


class DomainEventWriter:
    def __init__(self, domain, transaction_id, user_id, editor_organisation_id, event_repository):
        self._domain = domain
        self._transaction_id = transaction_id
        self._user_id = user_id
        self._editor_organisation_id = editor_organisation_id
        self._event_repository = event_repository
        self._already_flushed = False
        self._queued_event_aggregates = list()
        self._current_event_aggregate = None

    def write(self, entity_aggregate, event_type: UpdateType = None):
        """
        write event to the list to be published on flush.
        :param entity_aggregate:
        :param event_type:
        :return:
        """
        if not self._current_event_aggregate:
            self._current_event_aggregate = DomainEventFactory.create_event(self._domain, self._transaction_id,
                                                                            self._user_id, self._editor_organisation_id)
        self._current_event_aggregate.write(entity_aggregate, event_type)
        return self

    def flush(self):
        """
        queue the event to be saved for later.
        :return:
        """
        self._queued_event_aggregates.append(self._current_event_aggregate)
        self._current_event_aggregate = None

    def commit(self):
        """
        save all pending event aggregates to db
        """
        self._event_repository.save_all(self._queued_event_aggregates)
        self._queued_event_aggregates.clear()
