import os


class ElasticConfig:

    ELASTIC_HOST = os.environ.get("ELASTIC_HOST", "localhost:9200")
    ELASTIC_USE_SSL = os.environ.get("ELASTIC_USE_SSL", False)
    ELASTIC_VERIFY_SSL = os.environ.get("ELASTIC_VERIFY_SSL", False)
    ELASTIC_USERNAME = os.environ.get("ELASTIC_USERNAME", None)
    ELASTIC_PASSWORD = os.environ.get("ELASTIC_PASSWORD", None)

    def __init__(self, config=None):
        if config:
            self.ELASTIC_HOST = config["elastic_host"]
            self.ELASTIC_USERNAME = config["elastic_username"]
            self.ELASTIC_PASSWORD = config["elastic_password"]
            self.ELASTIC_USE_SSL = config.get("elastic_use_ssl", False)
            self.ELASTIC_VERIFY_SSL = config.get("elastic_verify_ssl", False)
