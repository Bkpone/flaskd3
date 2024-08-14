# coding=utf-8
"""
Base Repository
"""
import abc


class BaseRepository(object):
    """
    Base repository Interface
    """

    @property
    def name(self):
        return self.__class__.__name__

    @abc.abstractmethod
    def session(self):
        raise NotImplementedError("Session not Implemented for {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def save(self, item):
        raise NotImplementedError("save not Implemented for {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def update(self, item):
        raise NotImplementedError("update not Implemented for {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def update_all(self, items):
        raise NotImplementedError("update_all not Implemented for {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def save_all(self, items):
        raise NotImplementedError("save_all not Implemented for {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def filter(self, **kwargs):
        raise NotImplementedError("Session not Implemented for {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def filter_by(self, **kwargs):
        raise NotImplementedError("Session not Implemented for {}".format(self.__class__.__name__))

    @abc.abstractmethod
    def get(self, **kwargs):
        raise NotImplementedError("get not Implemented for {}".format(self.__class__.__name__))

    def get_for_update(self, **kwargs):
        raise NotImplementedError("get for update not Implemented for {}".format(self.__class__.__name__))

    def delete(self, item):
        raise NotImplementedError("delete not Implemented for {}".format(self.__class__.__name__))

    def delete_all(self, items):
        raise NotImplementedError("delete_all not Implemented for {}".format(self.__class__.__name__))

    def delete_by_query(self, **kwargs):
        raise NotImplementedError("delete_by_queries not Implemented for {}".format(self.__class__.__name__))

    def get_or_create(self, **kwargs):
        raise NotImplementedError("get_or_create not Implemented for {}".format(self.__class__.__name__))
