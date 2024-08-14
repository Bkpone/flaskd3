# coding=utf-8
"""
Queue service
"""
import logging

from kombu import Connection, Producer

from flaskd3.infrastructure.messaging.base_queue_service import BaseQueueService

logger = logging.getLogger(__name__)


class RabbitMQQueueService(BaseQueueService):
    """
    Queue service
    """

    def __init__(self, rabbitmq_url, exchange):
        self._rmq_url = rabbitmq_url
        logger.info("RabbitMQ url received: %s", self._rmq_url)
        self._conn = Connection(
            self._rmq_url,
            heartbeat=5,
            connect_timeout=15,
            transport_options={"confirm_publish": True},
        )
        self._exchange = exchange
        self._producer = Producer(channel=self._conn.channel(), exchange=self._exchange)

    def publish(self, payload, routing_key=None):
        # TODO move this to config after Bibek's config changes
        self._producer.publish(
            body=payload,
            routing_key=routing_key,
            retry_policy={
                "interval_start": 0,
                "interval_step": 2,
                "interval_max": 30,
                "max_retries": 3,
            },
            retry=True,
        )
