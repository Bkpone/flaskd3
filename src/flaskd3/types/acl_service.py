class ACLService:

    name = None

    @classmethod
    def get_name(cls):
        if not cls.name:
            cls.name = cls.__name__.lower().split("acl")[0]
        return cls.name
