import abc


class BaseDBService:
    @abc.abstractmethod
    def get_db(self):
        raise NotImplementedError("Get db must be implemented")

    @abc.abstractmethod
    def init_transaction(self):
        raise NotImplementedError("init transaction must be implemented")

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError("commit must be implemented")

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError("rollback must be implemented")
