from datetime import datetime

from flaskd3.types.base_entity import BaseEntity
from flaskd3.types.type_info import TypeInfo


class APIErrorLogAggregate(BaseEntity):
    error_log_id = TypeInfo(str, primary_key=True)
    created_at = TypeInfo(datetime)
    url = TypeInfo(str)
    payload = TypeInfo(dict)
    response_code = TypeInfo(str)
    message = TypeInfo(str)
    developer_message = TypeInfo(str)
    stacktrace = TypeInfo(str)
    error_code = TypeInfo(str)
