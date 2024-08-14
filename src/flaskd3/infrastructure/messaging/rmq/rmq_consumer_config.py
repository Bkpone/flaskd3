class RMQConsumerConfig(object):
    def __init__(
        self,
        rabbitmq_url,
        exchange_name,
        exchange_type,
        queue_name,
        routing_keys,
        exclusive,
        message_processor,
        auto_delete=False,
        durable=True,
        prefetch_count=10,
    ):
        self.rabbitmq_url = rabbitmq_url
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.queue_name = queue_name
        self.routing_keys = routing_keys
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.durable = durable
        self.message_processor = message_processor
        self.prefetch_count = prefetch_count
