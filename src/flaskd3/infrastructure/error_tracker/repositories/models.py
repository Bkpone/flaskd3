from flaskd3.infrastructure.database.sqlalchemy.orm_base import (
    db,
    DeleteMixin,
    TimeStampMixin,
    VersionMixin,
)


class APIErrorLogModel(db.Model, TimeStampMixin, DeleteMixin, VersionMixin):
    """
    Api error log entry model
    """

    __tablename__ = "api_error_log"

    error_log_id = db.Column("error_log_id", db.String(64), primary_key=True)
    url = db.Column("url", db.String(1024))
    payload = db.Column("payload", db.JSON)
    response_code = db.Column("response_code", db.String(64))
    message = db.Column("message", db.String(1024))
    developer_message = db.Column("developer_message", db.String(1024))
    stacktrace = db.Column("stacktrace", db.Text(16000000))
    error_code = db.Column("error_code", db.String(64))
