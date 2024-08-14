import logging
import json
from uuid import uuid4

from kombu import Connection, Exchange, binding, Queue
from kombu.mixins import ConsumerMixin

from flaskd3.infrastructure.messaging.base_consumer import BaseConsumer

logger = logging.getLogger(__name__)


class RMQConsumer(ConsumerMixin, BaseConsumer):
    """
    RMQ implementation of base consumer to be used to consume rmq messages. The application has to use this as the
    base to implement its own consumer.
    """

    def __init__(self, config):
        """
        :param config: The configuration object.
        """

        try:
            self._config = config
            self.connection = Connection(
                config.rabbitmq_url,
                connect_timeout=30,
                transport_options={"confirm_publish": True},
            )
            self.exchange = Exchange(config.exchange_name, type=config.exchange_type)
            bindings = []
            for routing_key in config.routing_keys:
                bindings.append(binding(self.exchange, routing_key=routing_key))
            self.queue = Queue(
                config.queue_name,
                bindings,
                exclusive=config.exclusive,
                durable=config.durable,
                auto_delete=config.auto_delete,
            )
            self.health_check_file = "/tmp/.rmq_consumer-{}".format(uuid4())
        except Exception:
            logger.exception("Error connecting to rabbitmq: %s: %s", config.rabbitmq_url)

    def process_message(self, body, message):
        try:
            response = self.get_message_processor().process_message(body)
            if response:
                message.ack()
                logger.info("Rmq message process completed. Message acknowledged.")
            else:
                message.reject(requeue=False)
                logger.info("Rmq message process process failure. Message rejected")
        except Exception:
            logger.exception("Could not process RMQ message. Message unacknowledged.")
            message.reject(requeue=True)

    def get_message_processor(self):
        return self._config.message_processor

    def get_consumers(self, consumer_class, channel):
        consumer = consumer_class(queues=[self.queue], callbacks=[self.process_message])
        consumer.qos(prefetch_count=self._config.prefetch_count)
        return [consumer]

    def stop_consumer(self):
        self.should_stop = True

    def start_consumer(self):
        try:
            self.run()
        except Exception as e:
            logging.critical(e)
