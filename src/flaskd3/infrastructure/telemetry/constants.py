from flaskd3.types.base_enum import BaseEnum


class TelemetryLogLevel(BaseEnum):
    INFO = "info", "Info"
    DEBUG = "debug", "Degub"
    WARN = "warn", "Warn"
    ERROR = "error", "Error"
