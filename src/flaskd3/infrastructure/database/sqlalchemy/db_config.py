import os

from urllib.parse import quote_plus


class DBConfig(object):

    @staticmethod
    def get_default_config():
        return {
            "db_password": "flaskd3",
            "db_user": "flaskd3",
            "db_master_url": "localhost",
            "db_slave_url": "localhost",
            "db_port": "3306",
            "db_name": "flaskd3",
            "ssh_tunnel_config": None,
            "is_password_temp": False,
            "migation_path": None
        }

    @staticmethod
    def get_config_from_os_env():
        db_config = dict()
        db_config_key_map = dict(
            db_password="DB_PASSWORD",
            db_user="DB_USER",
            db_master_url="DB_HOST",
            db_slave_url="DB_HOST",
            db_port="DB_PORT",
            db_name="DB_NAME",
            ssh_tunnel_config="SSH_TUNNEL_CONFIG",
            is_password_temp="IS_PASSWORD_TEMP",
            migation_path="MIGRATION_PATH",
        )
        for key, os_env_key in db_config_key_map.items():
            val = os.environ.get(os_env_key, None)
            if val is not None:
                db_config[key] = val
        return db_config

    def __init__(self, db_config_input):
        """
        DB Config order:
        Defaults || APP Config || OS Env || Env File
        :param db_config_input:
        """
        db_config = DBConfig.get_default_config()
        if db_config_input:
            db_config.update(db_config_input)
        self.DB_USER = db_config.get("db_user")
        self.DB_PASSWORD = db_config.get("db_password")
        self.DB_MASTER_URL = db_config.get("db_master_url")
        self.DB_SLAVE_URL = db_config.get("db_slave_url")
        self.DB_PORT = db_config.get("db_port")
        self.DB = db_config.get("db_name")
        self.SSH_TUNNEL_CONFIG = db_config.get("ssh_tunnel_config")
        self.is_password_temp = db_config.get("is_password_temp")
        self.migration_path = db_config.get("migration_path")

    def get_url(self):
        password_for_sql_url = quote_plus(self.DB_PASSWORD)
        return "mysql+mysqldb://%s:%s@%s:%s/%s" % (
            self.DB_USER,
            password_for_sql_url,
            self.DB_MASTER_URL,
            self.DB_PORT,
            self.DB,
        )
