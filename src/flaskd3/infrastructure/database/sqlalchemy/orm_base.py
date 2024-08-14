from sqlalchemy.sql import func

from flaskd3.infrastructure.database.sqlalchemy.common_models import AwareDateTime
from flaskd3.infrastructure.database.sqlalchemy.sql_db_service import db


class TimeStampMixin(object):
    """
    model for created time and modified time
    """

    created_at = db.Column("created_at", AwareDateTime, server_default=func.now(), nullable=False)
    modified_at = db.Column(
        "modified_at",
        AwareDateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DeleteMixin(object):
    deleted = db.Column("deleted", db.Boolean, default=False)


class VersionMixin(object):
    version = db.Column("version", db.Integer)


class MultiTenantMixin(object):
    tenant_id = db.Column("tenant_id", db.String(64))


class RelationshipMixin(object):
    relationship_id = db.Column("relationship_id", db.String(64), primary_key=True)
    status = db.Column("status", db.String(64))


class ListTyeDataInfo(object):
    def __init__(self, model_class, data_key):
        self.model_class = model_class
        self.data_key = data_key
