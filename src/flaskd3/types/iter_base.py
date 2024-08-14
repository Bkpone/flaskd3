import abc

from flaskd3.common.exceptions import InvalidStateException


class IterBase(object):
    @abc.abstractmethod
    def add(self, item):
        raise InvalidStateException("add Method Not implemented for Iter object {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def remove(self, item):
        raise InvalidStateException("remove Method Not implemented for Iter object {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def get(self, item):
        raise InvalidStateException("get Method Not implemented for Iter object {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def list(self):
        raise InvalidStateException("list Method Not implemented for Iter object {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def dirty(self):
        raise InvalidStateException("dirty Method Not implemented for Iter object {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def clear(self):
        raise InvalidStateException("clear Method Not implemented for Iter object {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def data(self):
        raise InvalidStateException("data Method Not implemented for Iter object {}".format(self.__class__.__name__))

    @property
    def is_dirty(self):
        raise InvalidStateException("is_dirty Method Not implemented for Iter object {}".format(self.__class__.__name__))

    def override(self, items):
        self.clear()
        for item in items:
            self.add(item)

    def update(self, items):
        self.clear()
        for item in items:
            self.add(item)

    def add_all(self, items):
        for item in items:
            self.add(item)
