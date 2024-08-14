from flaskd3.infrastructure.database.constants import DBType


class DBServiceProvider:
    def __init__(self):
        self.db_services = dict()

    def register_db_service(self, service_type, db_service):
        if not isinstance(service_type, DBType):
            raise ValueError("Invalid service type: {} should be of type DBType".format(type(service_type)))
        self.db_services[service_type] = db_service

    def get_db_service(self, service_type):
        return self.db_services.get(service_type)

    def init_transaction(self):
        for service in self.db_services.values():
            service.init_transaction()

    def commit(self):
        for service in self.db_services.values():
            service.commit()

    def rollback(self):
        for service in self.db_services.values():
            service.rollback()
