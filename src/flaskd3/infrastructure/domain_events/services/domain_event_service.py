import flask

from flaskd3.appcore.core.request_context import get_current_user, get_organisation_id
from flaskd3.infrastructure.domain_events.services.domain_event_writer import (
    DomainEventWriter,
)


class DomainEventService(object):
    def __init__(self, domain_event_repository):
        self._domain_event_repository = domain_event_repository
        self._domain_event_writers = dict()

    def create_domain_event_writer(self, domain):
        user = get_current_user()
        user_id = user.user_id if user else None
        request_id = getattr(flask.g, "request_id", None)
        return DomainEventWriter(
            domain,
            request_id,
            user_id,
            get_organisation_id(),
            self._domain_event_repository,
        )

    def get_event_writer_for_api(self, domain):
        domain_event_writer = self._domain_event_writers.get(domain)
        if not domain_event_writer:
            domain_event_writer = self.create_domain_event_writer(domain)
            self._domain_event_writers[domain] = domain_event_writer
        return domain_event_writer

    def get_event_by_id(self, event_id):
        return self._domain_event_repository.load(event_id)

    def get_events_by_transaction_id(self, transaction_id):
        return self._domain_event_repository.load_multiple(transaction_id=transaction_id)

    def commit_all(self):
        for _, event_writer in self._domain_event_writers.items():
            event_writer.commit()
        self._domain_event_writers.clear()
