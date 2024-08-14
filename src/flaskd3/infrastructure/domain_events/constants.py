from flaskd3.types.base_enum import BaseEnum


class DomainEventStatus(BaseEnum):
    CREATED = "created", "Created"
    PUBLISHED = "published", "Published"
    FAILED = "failed", "Failed"
    PROCESSED = "processed", "Processed"
    IGNORED = "ignored", "Ignored"
    RETRY_PENDING = "retry_pending", "Retry Pending"
    RETRYING = "retrying", "Retrying"


DOMAIN_EVENT_RMQ_EXCHANGE = "domain_events_exchange"
DOMAIN_EVENT_RMQ_EXCHANGE_TYPE = "topic"
