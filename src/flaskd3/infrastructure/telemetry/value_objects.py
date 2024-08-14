from flaskd3.types.value_object import ValueObject, ValueObjectField
from flaskd3.infrastructure.telemetry.constants import TelemetryLogLevel


class TelemetryLog(ValueObject):

    log_entry_id = ValueObjectField(str)
    log_level = ValueObjectField(TelemetryLogLevel)
    message = ValueObjectField(str)
    tags = ValueObjectField(str, many=True)
    key_tag = ValueObjectField(str)
    entity_name = ValueObjectField(str, required=False)
    entity_id = ValueObjectField(str, required=False)
    log_data = ValueObjectField(dict)


class ErrorLog(ValueObject):
    
    response_code = ValueObjectField(str)
    message = ValueObjectField(str)
    developer_message = ValueObjectField(str)
    stacktrace = ValueObjectField(str)
    error_code = ValueObjectField(str)