from flaskd3.infrastructure.database.sqlalchemy.orm_base import (
    db,
    DeleteMixin,
    TimeStampMixin,
)


class IDGenerator(db.Model, TimeStampMixin, DeleteMixin):
    """IDGenerator model"""

    __tablename__ = "idgenerator"

    id = db.Column(db.Integer, primary_key=True)
    scope = db.Column(db.String(40), unique=True)
    counter = db.Column(db.BigInteger)
