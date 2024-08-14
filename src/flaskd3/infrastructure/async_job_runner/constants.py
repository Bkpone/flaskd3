from flaskd3.types.base_enum import BaseEnum


class AsyncJobTypes(BaseEnum):
    RECURRING = "recurring", "Recurring"
    ONE_TIME = "one_time", "One Time"


class AsyncJobStatus(BaseEnum):
    CREATED = "created", "Created"
    ENQUEUE = "enqueue", "Enqueue"
    PROCESSING = "processing", "Processing"
    FAILED = "failed", "Failed"
    FINISHED = "finished", "Finished"
    CLOSED = "closed", "Closed"


class IntervalUnit(BaseEnum):
    SECONDS = "seconds", "Seconds"
    MINUTES = "minutes", "Minutes"
    HOURS = "hours", "Hours"
    DAYS = "days", "Days"
    WEEKS = "weeks", "Weeks"
    MONTHS = "Months"
    DAY = "day", "Day"


JOBS_RMQ_EXCHANGE = "async_job_exchange"
JOBS_RMQ_EXCHANGE_TYPE = "direct"
JOBS_ROUTING_KEY = "async_job"
