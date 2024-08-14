from kombu import Exchange

from flaskd3.infrastructure.domain_events.constants import (
    DOMAIN_EVENT_RMQ_EXCHANGE,
    DOMAIN_EVENT_RMQ_EXCHANGE_TYPE,
)
from flaskd3.infrastructure.messaging.rmq.rmq_queue_service import RabbitMQQueueService
from flaskd3.common.utils.common_utils import convert_key_to_camel_case
from flaskd3.common.utils.json_utils import make_jsonify_ready


class DomainEventRMQPublisher(RabbitMQQueueService):
    def __init__(self, rabbitmq_url):
        super(DomainEventRMQPublisher, self).__init__(
            rabbitmq_url,
            Exchange(
                DOMAIN_EVENT_RMQ_EXCHANGE,
                type=DOMAIN_EVENT_RMQ_EXCHANGE_TYPE,
                durable=True,
            ),
        )

    def publish(self, event_aggregate):
        routing_key = "{}".format(event_aggregate.domain)
        message = event_aggregate.message()
        converted_message = convert_key_to_camel_case(message)
        message = make_jsonify_ready(converted_message)
        super().publish(message, routing_key)
