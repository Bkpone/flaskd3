from datetime import datetime

from flaskd3.infrastructure.database.sqlalchemy.common_models import AwareDateTime
from flaskd3.infrastructure.database.sqlalchemy.orm_base import (
    db,
    DeleteMixin,
    TimeStampMixin,
    VersionMixin, MultiTenantMixin,
)


class JobModel(db.Model, TimeStampMixin, DeleteMixin, VersionMixin, MultiTenantMixin):
    __tablename__ = "job"

    job_id = db.Column("job_id", db.String(64), primary_key=True)
    extra_data = db.Column("extra_data", db.JSON)
    job_name = db.Column("job_name", db.String(64))
    status = db.Column("status", db.String(64), nullable=False)
    run_time = db.Column("run_time", db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    response = db.Column("response", db.Text(64000))
    tries = db.Column("total_tries", db.Integer, default=0, nullable=False)


class RecurringJobModel(db.Model, TimeStampMixin, DeleteMixin, VersionMixin, MultiTenantMixin):
    __tablename__ = "recurring_job"

    recurring_job_id = db.Column("recurring_job_id", db.String(64), primary_key=True)
    extra_data = db.Column("extra_data", db.JSON)
    name = db.Column("name", db.String(64))
    job_name = db.Column("job_name", db.String(64))
    is_active = db.Column("is_active", db.Boolean)
    status = db.Column("status", db.String(64), nullable=False)
    schedule_pending = db.Column("schedule_pending", db.Boolean)
    last_run_datetime = db.Column("last_run_datetime", AwareDateTime)
    next_run_datetime = db.Column("next_run_datetime", AwareDateTime)
    schedule = db.Column("schedule", db.JSON)


class RecurringJobRunLogModel(db.Model, TimeStampMixin, DeleteMixin, VersionMixin, MultiTenantMixin):
    __tablename__ = "recurring_job_run_log"

    recurring_job_run_log_id = db.Column("recurring_job_run_log_id", db.String(64), primary_key=True)
    recurring_job_id = db.Column("recurring_job_id", db.String(64))
    job_id = db.Column("job_id", db.String(64))
    status = db.Column("status", db.String(64), nullable=False)
    run_datetime = db.Column("run_datetime", AwareDateTime)
