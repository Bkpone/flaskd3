import os


def setup_config(app, config_module_map=None):
    """
    :return:
    """
    environment = os.environ.get("APP_ENV", "local")
    if config_module_map:
        config_module = config_module_map.get(environment)
        if config_module:
            app.config.from_object(config_module)
    config_file_path = os.environ.get("JSON_CONFIG_FILE_PATH", None)
    if config_file_path:
        app.config.from_json(config_file_path, True)
        print("Loaded config from {}".format(config_file_path))
    if app.config["ENABLE_PROFILING"]:
        app.config["PREF_OUTPUT"] = open(os.path.join(app.config["LOG_ROOT"], app.config["PERF_FILE_NAME"]), "w")
        app.config["SQLALCHEMY_RECORD_QUERIES"] = True
