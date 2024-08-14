from flaskd3.types.value_object import ValueObject


class DomainEventData(ValueObject):
    def __init__(self, entity, entity_id, version, event_type, event_data):
        self.event_data = event_data
        self.event_type = event_type
        self.version = version
        self.entity_id = entity_id
        self.entity = entity
