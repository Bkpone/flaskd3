from datetime import datetime

from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.type_info import TypeInfo
from flaskd3.infrastructure.domain_events.constants import DomainEventStatus
from flaskd3.infrastructure.domain_events.value_objects import DomainEventData
from flaskd3.common.constants import UpdateType
from flaskd3.common.exceptions import InvalidStateException, ValidationException
from flaskd3.common.utils.json_utils import make_jsonify_ready


class DomainEventAggregate(BaseEntity):

    event_id = TypeInfo(str, primary_key=True)
    domain = TypeInfo(str)
    transaction_id = TypeInfo(str, required=False)
    updates = TypeInfo(DomainEventData, many=True)
    generated_at = TypeInfo(datetime)
    user_id = TypeInfo(str)
    editor_organisation_id = TypeInfo(str)
    status = TypeInfo(DomainEventStatus, required=False, default=DomainEventStatus.CREATED)

    def add_event(self, event_data):
        self.updates.add(event_data)

    def message(self):
        event_data = [entry.dict() for entry in self.updates]
        return_dict = dict(
            event_id=self.event_id,
            domain=self.domain,
            transaction_id=self.transaction_id,
            user_id=self.user_id,
            editor_organisation_id=self.editor_organisation_id,
            generated_at=self.generated_at,
            updates=event_data,
        )
        return return_dict

    def has_data(self):
        return len(self.updates) > 0

    def write(self, entity_aggregate, event_type: UpdateType = None):
        """
        write event to the list to be published on flush.
        :param entity_aggregate:
        :param event_type:
        :return:
        """

        if not isinstance(entity_aggregate, BaseEntity):
            raise ValidationException(message="Can only add Base entity type to domain event.")

        if not event_type:
            if entity_aggregate.version == 1:
                event_type = UpdateType.CREATED
            elif entity_aggregate.deleted:
                event_type = UpdateType.DELETED
            elif entity_aggregate.has_actions:
                event_type = UpdateType.ACTION
            else:
                event_type = UpdateType.UPDATED

        if event_type == UpdateType.CREATED:
            data = make_jsonify_ready(entity_aggregate.data())
        elif event_type == UpdateType.UPDATED:
            data = make_jsonify_ready(entity_aggregate.dirty())
        elif event_type == UpdateType.DELETED:
            data = make_jsonify_ready(entity_aggregate.data())
        elif event_type == UpdateType.ACTION:
            data = make_jsonify_ready(entity_aggregate.get_actions_update())
        else:
            raise InvalidStateException(description="Invalid event type.")
        event_data = DomainEventData(
            entity=entity_aggregate.unique_name,
            entity_id=entity_aggregate.primary_id,
            version=entity_aggregate.get_latest_version(),
            event_type=event_type,
            event_data=data,
        )
        self.add_event(event_data)
        return self

