from abc import abstractmethod


class BaseMessageProcessor(object):
    @abstractmethod
    def process_message(self, message_data):
        NotImplemented("process message function not implemented.")
