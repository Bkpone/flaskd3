from abc import abstractmethod


class BaseConsumer(object):
    """
    The Base consumer to be implemented by any consumer provider like RNQ etc.
    """

    @abstractmethod
    def process_message(self, body, message):
        raise NotImplemented("The implementation missing for process_message.")

    @abstractmethod
    def start_consumer(self):
        raise NotImplemented("The implementation missing for start_consumer.")

    @abstractmethod
    def get_message_processor(self):
        raise NotImplemented("The implementation missing for get_message_handler.")
