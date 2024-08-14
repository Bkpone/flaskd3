import os

from urllib.parse import quote_plus


class DBConfig(object):

    @staticmethod
    def get_default_config():
        return {
            "db_password": os.environ.get("DB_PASSWORD", "flaskd3"),
            "db_user": os.environ.get("DB_USER", "flaskd3"),
            "db_master_url": os.environ.get("DB_HOST", "localhost"),
            "db_slave_url": os.environ.get("DB_HOST", "localhost"),
            "db_port": os.environ.get("DB_PORT", "3306"),
            "db_name": os.environ.get("DB_NAME", "flaskd3"),
            "ssh_tunnel_config": os.environ.get("SSH_TUNNEL_CONFIG", None),
            "is_password_temp": os.environ.get("IS_PASSWORD_TEMP", False)
        }

    def __init__(self, db_config_input):
        db_config = DBConfig.get_default_config()
        if db_config_input:
            db_config.update(db_config_input)
        self.DB_USER = db_config.get("db_user")
        self.DB_PASSWORD = db_config.get("db_password")
        self.DB_MASTER_URL = db_config.get("db_host")
        self.DB_SLAVE_URL = db_config.get("db_host")
        self.DB_PORT = db_config.get("db_port")
        self.DB = db_config.get("db_name")
        self.SSH_TUNNEL_CONFIG = db_config.get("ssh_tunnel_config")
        self.is_password_temp = db_config.get("is_password_temp")

    def get_url(self):
        password_for_sql_url = quote_plus(self.DB_PASSWORD)
        return "mysql+mysqldb://%s:%s@%s:%s/%s" % (
            self.DB_USER,
            password_for_sql_url,
            self.DB_MASTER_URL,
            self.DB_PORT,
            self.DB,
        )
