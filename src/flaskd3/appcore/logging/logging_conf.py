# coding=utf-8
"""
LOGGING CONF
"""
import os


def configure_logging(app):
    """
    Logging Setup
    :param app:
    :return:
    """
    import logging.config

    environment = os.environ.get("APP_ENV", "local")

    logging_conf = {
        "version": 1,
        "filters": {"request_id": {"()": "flaskd3.appcore.core.logging.log_filters.RequestIdFilter"}},
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(asctime)s] %(levelname)s %(request_id)s - [%(name)s:%(" "lineno)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "logstash": {"()": "logstash_formatter.LogstashFormatterV1"},
        },
        "handlers": {
            "null": {
                "level": "DEBUG",
                "class": "logging.NullHandler",
                "filters": ["request_id"],
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
                "filters": ["request_id"],
            },
            "flaskd3": {
                "level": "DEBUG",
                "class": "logging.handlers.WatchedFileHandler",
                "filename": os.path.join(app.config["LOG_ROOT"], app.config["LOG_PATH"]),
                "formatter": "verbose",
                #'formatter': 'logstash' if environment == 'prod' else 'verbose',
                "filters": ["request_id"],
            },
            "flaskd3_error": {
                "level": "ERROR",
                "class": "logging.handlers.WatchedFileHandler",
                "filename": os.path.join(app.config["LOG_ROOT"], app.config["ERROR_LOG_PATH"]),
                "formatter": "verbose",
                #'formatter': 'logstash' if environment == 'prod' else 'verbose',
                "filters": ["request_id"],
            },
            "request": {
                "level": "DEBUG",
                "class": "logging.handlers.WatchedFileHandler",
                "filename": app.config["LOG_ROOT"] + "/request.log",
                "formatter": "logstash" if environment == "prod" else "verbose",
                "filters": ["request_id"],
            },
        },
        "loggers": {
            "flaskd3": {
                "handlers": ["console", "flaskd3", "flaskd3_error"],
                "level": "DEBUG" if environment == "prod" else "DEBUG",
                "propagate": False,
            },
            "": {
                "handlers": ["console", "flaskd3", "flaskd3_error"],
                "level": "ERROR",
            },
            "root": {
                "handlers": ["console", "flaskd3", "flaskd3_error"],
                "level": "ERROR",
            },
            "request_handler": {
                "handlers": ["console", "request"],
                "level": "INFO" if environment == "prod" else "DEBUG",
                "propagate": False,
            },
        },
    }
    logging.config.dictConfig(logging_conf)
