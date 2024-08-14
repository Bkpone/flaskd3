from abc import ABC, abstractmethod


class BaseQueueService(ABC):
    """
    Queue service
    """

    @abstractmethod
    def publish(self, data, **attributes):
        # Setup Exchange and queues
        pass
