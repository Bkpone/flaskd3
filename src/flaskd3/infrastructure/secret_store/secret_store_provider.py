from flaskd3.infrastructure.secret_store.base_secret_store import BaseSecretStore


class SecretStoreProvider:

    secret_store_class_map = {
        "base": BaseSecretStore
    }

    def __init__(self, secret_store_configs, default_secret_store="base"):
        self.handler_registry = dict(base=self.secret_store_class_map.get("base")(None))
        for name, secret_store_config in secret_store_configs:
            self.handler_registry[name] = self.secret_store_class_map.get(name)(secret_store_config)
        self.default_secret_store = self.get_handler(default_secret_store)

    def get_handler(self, store_name):
        return self.handler_registry.get(store_name)

    def get_default(self):
        return self.default_secret_store

    def register(self, store_handler_class):
        self.secret_store_class_map[store_handler_class.NAME] = store_handler_class
