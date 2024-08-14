from kombu import Exchange

from flaskd3.infrastructure.async_job_runner.constants import (
    JOBS_RMQ_EXCHANGE,
    JOBS_RMQ_EXCHANGE_TYPE, JOBS_ROUTING_KEY,
)
from flaskd3.infrastructure.messaging.rmq.rmq_queue_service import RabbitMQQueueService


class JobRMQPublisher(RabbitMQQueueService):
    def __init__(self, rabbitmq_url):
        super(JobRMQPublisher, self).__init__(
            rabbitmq_url,
            Exchange(JOBS_RMQ_EXCHANGE, type=JOBS_RMQ_EXCHANGE_TYPE, durable=True),
        )

    def publish(self, job_aggregate):
        routing_key = "{}-{}".format(JOBS_ROUTING_KEY, job_aggregate.tenant_id)
        super().publish(job_aggregate.job_id, routing_key)
