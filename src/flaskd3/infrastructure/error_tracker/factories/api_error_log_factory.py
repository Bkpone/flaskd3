from flaskd3.common.utils.id_generator_utils import generate_id_with_prefix
from flaskd3.infrastructure.error_tracker.aggregates.api_error_log_aggregate import (
    APIErrorLogAggregate,
)


class APIErrorLogFactory:
    @staticmethod
    def create_log_entry(url, payload, response_code, message, developer_message, stacktrace, error_code):
        error_log_id = generate_id_with_prefix("ERR")
        return APIErrorLogAggregate(
            error_log_id=error_log_id,
            url=url,
            payload=payload,
            response_code=str(response_code),
            message=message,
            developer_message=developer_message,
            stacktrace=stacktrace,
            error_code=str(error_code),
        )

    @staticmethod
    def create_entry_from_data(data):
        return APIErrorLogAggregate(
            error_log_id=data.get("error_log_id"),
            url=data.get("url"),
            payload=data.get("payload"),
            response_code=data.get("response_code"),
            message=data.get("message"),
            developer_message=data.get("developer_message"),
            stacktrace=data.get("stacktrace"),
            error_code=data.get("error_code"),
        )
