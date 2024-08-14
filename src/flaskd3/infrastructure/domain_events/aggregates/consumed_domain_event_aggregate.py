from datetime import datetime

from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.type_info import TypeInfo
from flaskd3.infrastructure.domain_events.constants import DomainEventStatus
from flaskd3.infrastructure.domain_events.value_objects import DomainEventData


class ConsumedDomainEventAggregate(BaseEntity):

    event_id = TypeInfo(str, primary_key=True)
    domain = TypeInfo(str)
    transaction_id = TypeInfo(str, required=False)
    raw_updates = TypeInfo(dict, many=True)
    updates = TypeInfo(DomainEventData, many=True, required=False)
    generated_at = TypeInfo(datetime)
    user_id = TypeInfo(str)
    editor_organisation_id = TypeInfo(str)
    status = TypeInfo(DomainEventStatus, required=False, default=DomainEventStatus.CREATED)
    details = TypeInfo(str, allow_none=True, required=False)
