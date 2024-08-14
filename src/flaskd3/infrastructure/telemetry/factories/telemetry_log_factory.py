from flaskd3.common.utils.id_generator_utils import generate_id_with_prefix
from flaskd3.common.utils.dateutils import current_datetime
from flaskd3.infrastructure.telemetry.aggregates.telemetry_log_aggregate import TelemetryLogAggregate


class TelemetryLogFactory:
    @staticmethod
    def create_telemetry_log(url, request_id, headers, payload):
        telemetry_id = generate_id_with_prefix("TEL")
        return TelemetryLogAggregate(
            telemetry_id=telemetry_id,
            started_at=current_datetime(),
            url=url,
            request_id=request_id,
            headers=headers,
            payload=payload
        )
