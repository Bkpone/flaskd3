import logging

from flaskd3.infrastructure.messaging.base_queue_service import BaseQueueService

logger = logging.getLogger(__name__)


class DummyQueueService(BaseQueueService):
    """
    Queue service
    """

    def init(self, app, config=None):
        pass

    def publish(self, data, **attributes):
        # Setup Exchange and queues
        logger.log("Got message with data: {} and attributed: {}".format(data, attributes))
        return
