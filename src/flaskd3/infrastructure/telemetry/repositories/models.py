from flaskd3.infrastructure.database.sqlalchemy.common_models import AwareDateTime
from flaskd3.infrastructure.database.sqlalchemy.orm_base import (
    db,
    DeleteMixin,
    TimeStampMixin,
    VersionMixin,
)


class TelemetryLogModel(db.Model, TimeStampMixin, DeleteMixin, VersionMixin):
    """
    Telemetry model
    """

    __tablename__ = "telemetry"

    telemetry_id = db.Column("telemetry_id", db.String(64), primary_key=True)
    url = db.Column("url", db.String(64))
    started_at = db.Column("started_at", AwareDateTime)
    payload = db.Column("payload", db.JSON)
    request_id = db.Column("request_id", db.String(64))
    user_id = db.Column("user_id", db.String(64))
    headers = db.Column("headers", db.JSON)
    payload = db.Column("payload", db.JSON)
    logs = db.Column("logs", db.JSON)
    response = db.Column("response", db.JSON)
    exception = db.Column("exception", db.JSON)
