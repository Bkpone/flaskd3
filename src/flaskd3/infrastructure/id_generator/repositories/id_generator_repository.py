from flaskd3.infrastructure.database.sqlalchemy.sql_base_aggregate_repository import (
    SQLABaseAggregateRepository,
)
from flaskd3.infrastructure.id_generator.models import IDGenerator


class IDGeneratorRepository(SQLABaseAggregateRepository):
    name = "id_generator_repository"

    def generate_id(self, scope):
        idgenerator = self.get_for_update(IDGenerator, False, scope=scope)
        if not idgenerator:
            idgenerator = IDGenerator(scope=scope, counter=1)
            self._save(idgenerator)
        else:
            idgenerator.counter += 1
            self._update(idgenerator)
        return str(idgenerator.counter)
