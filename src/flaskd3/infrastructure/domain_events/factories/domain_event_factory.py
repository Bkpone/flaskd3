from datetime import datetime

from flaskd3.common.utils.dateutils import current_datetime
from flaskd3.common.utils.id_generator_utils import generate_id_with_prefix
from flaskd3.types.constants import CoreDataTypes
from flaskd3.infrastructure.domain_events.aggregates.consumed_domain_event_aggregate import (
    ConsumedDomainEventAggregate,
)
from flaskd3.infrastructure.domain_events.aggregates.domain_event_aggregate import (
    DomainEventAggregate,
)
from flaskd3.common.constants import UpdateType
from flaskd3.infrastructure.domain_events.value_objects import DomainEventData
from flaskd3.common.value_objects import ActionLog
from flaskd3.common.utils.common_utils import convert_key_to_snake_case


class DomainEventFactory:

    entity_schema_map = {}

    @staticmethod
    def create_event(domain, transaction_id, user_id, editor_organisation_id):
        event_id = generate_id_with_prefix("DE", domain)
        event = DomainEventAggregate(
            event_id=event_id,
            domain=domain,
            transaction_id=transaction_id,
            generated_at=current_datetime(),
            updates=[],
            user_id=user_id,
            editor_organisation_id=editor_organisation_id,
        )
        return event

    @staticmethod
    def create_domain_event_from_data(event_data):
        generated_at = datetime.strptime(event_data.get("generatedAt"), "%Y-%m-%dT%H:%M:%S%z")
        aggregate = ConsumedDomainEventAggregate(
            event_id=event_data.get("eventId"),
            domain=event_data.get("domain"),
            transaction_id=event_data.get("transactionId"),
            generated_at=generated_at,
            raw_updates=event_data.get("updates"),
            user_id=event_data.get("userId"),
            editor_organisation_id=event_data.get("editorOrganisationId"),
        )
        return aggregate

    @staticmethod
    def parse_events(event_datas):
        updates = []
        for event_data in event_datas:
            event_type = UpdateType(event_data.get("eventType"))
            entity_schema = DomainEventFactory.entity_schema_map.get(event_data.get("entity"))
            data_attributes = dict(
                entity=event_data.get("entity"),
                entity_id=event_data.get("entityId"),
                version=event_data.get("version"),
                event_type=event_type,
            )
            data_json_obj = event_data.get("eventData")
            if data_json_obj:
                if event_type in [UpdateType.CREATED, UpdateType.DELETED]:
                    data_attributes["event_data"] = entity_schema(unknown="IGNORE").load(data_json_obj)
                elif event_type == UpdateType.ACTION:
                    data = dict(
                        id=data_json_obj["update"]["id"],
                        type=CoreDataTypes(data_json_obj["update"]["type"]),
                    )
                    data["data"] = dict(
                        actions=[ActionLog(**convert_key_to_snake_case(data_json_obj["actions"][1]))],
                        update=DomainEventFactory._parse_entity_data(data_json_obj["update"], entity_schema)
                        if entity_schema
                        else data_json_obj["update"],
                    )
                    data_attributes["event_data"] = data
                else:
                    data = dict(
                        id=data_json_obj["id"],
                        type=CoreDataTypes(data_json_obj["type"]),
                    )
                    data["data"] = (
                        DomainEventFactory._parse_entity_data(data_json_obj["data"], entity_schema) if entity_schema else data_json_obj["data"]
                    )
                    data_attributes["event_data"] = data
            else:
                data_attributes["event_data"] = None
            updates.append(DomainEventData(**data_attributes))
        return updates

    @staticmethod
    def _parse_value(value, value_field):
        value_type = value.get("type")
        ret_dict = dict(value_type=value_type)
        if value_type == CoreDataTypes.ENTITY.value:
            ret_dict["id"] = value["id"]
            ret_dict["data"] = DomainEventFactory._parse_entity_data(value["data"], value_field.schema.__class__)
            return ret_dict
        elif value_type == CoreDataTypes.ENTITY_LIST.value:
            ret_dict["data"] = DomainEventFactory._parse_entity_list(value["data"], value_field)
        elif value_type == CoreDataTypes.LIST.value:
            ret_dict["data"] = DomainEventFactory._parse_list(value["data"], value_field)
        elif value_type == CoreDataTypes.SET.value:
            ret_dict["data"] = DomainEventFactory._parse_set(value["data"], value_field)
        else:
            ret_dict["data"] = DomainEventFactory._parse_generic(value["data"], value_field)
        return ret_dict

    @staticmethod
    def _parse_entity_data(data, schema):
        schema_attributes = schema._declared_fields
        parsed_entity = dict()
        for key, value in data.items():
            value_field = schema_attributes.get(key)
            if value_field:
                key = value_field.attribute if value_field.attribute else key
                parsed_entity[key] = DomainEventFactory._parse_value(value, value_field)
        return parsed_entity

    @staticmethod
    def _parse_value_object(data, value_field):
        return dict(
            old=value_field.schema.load(data["old"], many=False, unknown="IGNORE"),
            new=value_field.schema.load(data["new"], many=False, unknown="IGNORE"),
        )

    @staticmethod
    def _parse_generic(data, value_field):
        return dict(
            old=value_field.deserialize(data["old"]),
            new=value_field.deserialize(data["new"]),
        )

    @staticmethod
    def _parse_entity_list(data, field_data):
        schema = field_data.schema
        ret_dict = dict()
        ret_dict["added"] = list()
        ret_dict["deleted"] = list()
        ret_dict["updated"] = list()
        for entry in data["added"]:
            ret_dict["added"].append(schema.load(entry, many=False, unknown="IGNORE"))
        for entry in data["deleted"]:
            ret_dict["deleted"].append(schema.load(entry, many=False, unknown="IGNORE"))
        for entry in data["updated"]:
            ret_dict["updated"].append(DomainEventFactory._parse_value(entry, field_data))
        return ret_dict

    @staticmethod
    def _parse_list(data, field_data):
        ret_dict = dict()
        ret_dict["added"] = field_data.deserialize(data["added"])
        ret_dict["deleted"] = field_data.deserialize(data["deleted"])
        return ret_dict

    @staticmethod
    def _parse_set(data, field_data):
        ret_dict = dict()
        ret_dict["added"] = set(field_data.deserialize(data["added"]))
        ret_dict["deleted"] = set(field_data.deserialize(data["deleted"]))
        return ret_dict
