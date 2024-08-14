class IDGeneratorService(object):
    def __init__(self, id_generator_repository):
        self.id_generator_repository = id_generator_repository

    def generate_id(self, scope, suffix=None):
        id_count = self.id_generator_repository.generate_id(scope)
        return "{}{}".format(suffix, id_count) if suffix else str(id_count)
