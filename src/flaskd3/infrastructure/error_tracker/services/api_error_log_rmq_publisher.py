from kombu import Exchange

from flaskd3.infrastructure.error_tracker.constants import (
    API_ERROR_LOG_RMQ_EXCHANGE,
    API_ERROR_LOG_RMQ_EXCHANGE_TYPE,
    API_ERROR_ROUTING_KEY,
)
from flaskd3.infrastructure.messaging.rmq.rmq_queue_service import RabbitMQQueueService
from flaskd3.common.utils.json_utils import make_jsonify_ready


class APIErrorLogRMQPublisher(RabbitMQQueueService):
    def __init__(self, rabbitmq_url):
        super(APIErrorLogRMQPublisher, self).__init__(
            rabbitmq_url,
            Exchange(
                API_ERROR_LOG_RMQ_EXCHANGE,
                type=API_ERROR_LOG_RMQ_EXCHANGE_TYPE,
                durable=True,
            ),
        )

    def publish(self, error_aggregate):
        routing_key = API_ERROR_ROUTING_KEY
        message = make_jsonify_ready(error_aggregate.data())
        super().publish(message, routing_key)
