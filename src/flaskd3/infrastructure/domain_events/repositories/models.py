from flaskd3.infrastructure.database.sqlalchemy.common_models import AwareDateTime
from flaskd3.infrastructure.database.sqlalchemy.orm_base import (
    db,
    TimeStampMixin,
    DeleteMixin,
    VersionMixin,
)


class DomainEventModel(db.Model, TimeStampMixin, DeleteMixin, VersionMixin):
    """Domain event model"""

    __tablename__ = "domain_event"

    event_id = db.Column("event_id", db.String(64), primary_key=True)
    domain = db.Column("domain", db.String(64))
    transaction_id = db.Column("transaction_id", db.String(64))
    generated_at = db.Column("generated_at", AwareDateTime)
    updates = db.Column("updates", db.JSON)
    status = db.Column("status", db.String(64))
    user_id = db.Column("user_id", db.String(64))
    editor_organisation_id = db.Column("editor_organisation_id", db.String(64))


class ConsumedDomainEventModelMixin(TimeStampMixin, DeleteMixin, VersionMixin):
    """Consumed Domain event model"""

    event_id = db.Column("event_id", db.String(64), primary_key=True)
    domain = db.Column("domain", db.String(64))
    transaction_id = db.Column("transaction_id", db.String(64))
    generated_at = db.Column("generated_at", AwareDateTime)
    updates = db.Column("updates", db.JSON)
    raw_updates = db.Column("raw_updates", db.JSON)
    status = db.Column("status", db.String(64))
    details = db.Column("details", db.Text(1600000))
    user_id = db.Column("user_id", db.String(64))
    editor_organisation_id = db.Column("editor_organisation_id", db.String(64))
