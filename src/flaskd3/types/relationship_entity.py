from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.state_machine import StateMachineFactory, StateTransition
from flaskd3.types.type_info import TypeInfo
from flaskd3.common.constants import RelationshipStatus, RelationshipAction
from flaskd3.common.exceptions import InvalidStateException, ValidationException
from flaskd3.common.utils.id_generator_utils import generate_id_with_prefix


class RelationshipTypeInfo(TypeInfo):

    def __init__(self, relationship_entity, **kwargs):
        self.relationship_entity = relationship_entity
        if "class_obj" in kwargs.keys():
            raise InvalidStateException(message="Relationship key type can be only of type str")
        super(RelationshipTypeInfo, self).__init__(class_obj=str, **kwargs)


class RelationshipEntity(BaseEntity):

    _parent_attributes = {
        "relationship_id": TypeInfo(str, primary_key=True),
        "status": TypeInfo(RelationshipStatus)
    }

    state_machine_factory = StateMachineFactory(
        state_key="status",
        transitions=[
            StateTransition(
                trigger=RelationshipAction.RAISE_REVIEW,
                source=[RelationshipStatus.CREATED, RelationshipStatus.REJECTED],
                destination=RelationshipStatus.IN_REVIEW,
            ),
            StateTransition(
                trigger=RelationshipAction.APPROVE,
                source=[RelationshipStatus.IN_REVIEW],
                destination=RelationshipStatus.APPROVED,
            ),
            StateTransition(
                trigger=RelationshipAction.REJECT,
                source=[RelationshipStatus.CREATED, RelationshipStatus.IN_REVIEW],
                destination=RelationshipStatus.REJECTED,
            ),
            StateTransition(
                trigger=RelationshipAction.ACTIVATE,
                source=[RelationshipStatus.CREATED, RelationshipStatus.APPROVED],
                destination=RelationshipStatus.ACTIVE,
            ),
            StateTransition(
                trigger=RelationshipAction.DEACTIVATE,
                source=[RelationshipStatus.CREATED, RelationshipStatus.IN_REVIEW,
                        RelationshipStatus.APPROVED, RelationshipStatus.REJECTED,
                        RelationshipStatus.ACTIVE],
                destination=RelationshipStatus.DEACTIVATED,
            )
        ],
    )

    @classmethod
    def relationship_entities(cls):
        relationship_entities = dict()
        for attr_name, e in cls.get_attributes().items():
            if isinstance(e, RelationshipTypeInfo):
                relationship_entities[attr_name] = e
        return relationship_entities

    @classmethod
    def make_relationship(cls, entity_1, entity_2, status=RelationshipStatus.ACTIVE):
        mapped_entities_names = [e.relationship_entity.entity_name() for attr_name, e in
                                 cls.relationship_entities().items()]
        if entity_1.entity_name() not in mapped_entities_names or entity_2.entity_name() not in mapped_entities_names:
            raise ValidationException(message="Invalid entity given to relationship",
                                      extra_payload=dict(entity_1=entity_1.get_name(),
                                                         entity_2=entity_2.get_name(),
                                                         relationship=cls.__name__))
        tenant_1 = tenant_2 = None
        if entity_1.is_multi_tenant:
            tenant_1 = entity_1.tenant_id
        if entity_2.is_multi_tenant:
            tenant_2 = entity_2.tenant_id
        if (tenant_1 or tenant_2) and (tenant_1 != tenant_2):
            raise ValidationException(message="Both entity to be create relationship with should have same tenant.")
        params = dict(relationship_id=generate_id_with_prefix("REL"), status=status)
        if tenant_1:
            params["tenant_id"] = tenant_1
        params[entity_1.get_primary_key()] = entity_1.primary_id
        params[entity_2.get_primary_key()] = entity_2.primary_id
        return cls(**params)

