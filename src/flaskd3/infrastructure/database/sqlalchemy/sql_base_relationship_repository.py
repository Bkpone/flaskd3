import logging

from flaskd3.infrastructure.database.sqlalchemy.sql_base_aggregate_repository import SQLABaseAggregateRepository
from flaskd3.common.exceptions import (
    ValidationException
)

logger = logging.getLogger(__name__)


class SQLABaseRelationshipRepository(SQLABaseAggregateRepository):

    def find_all(self, entity_1, status=None, meta=None):
        params = dict()
        lhs_entity_key = rhs_entity_key = None
        if status:
            params[status] = status
        for key, type_info in self.aggregate_class.relationship_entities().items():
            entity = type_info.relationship_entity
            if entity.entity_name() == entity_1.entity_name():
                lhs_entity_key = key
            else:
                rhs_entity_key = key
        if not lhs_entity_key:
            raise ValidationException(message="Invalid entity given to relationship",
                                      extra_payload=dict(entity_1=entity_1.entity_name(),
                                                         entity_2=rhs_entity_key,
                                                         relationship=self.aggregate_class.entity_name()))
        params[lhs_entity_key] = entity_1.primary_id
        if entity_1.is_multi_tenant:
            params["tenant_id"] = entity_1.tenant_id
        return self.load_by_keys(meta=meta, **params)
