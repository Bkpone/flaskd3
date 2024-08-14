class ApplicationService:

    name = None

    @classmethod
    def get_name(cls):
        if not cls.name:
            cls.name = cls.__name__.lower().split("applicationservice")[0]
        return cls.name
