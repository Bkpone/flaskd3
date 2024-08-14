import hashlib
import logging
import json
from collections import defaultdict

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy, event, get_debug_queries
from sqlalchemy.engine.base import Engine

from flaskd3.infrastructure.database.sqlalchemy.db_config import DBConfig
from flaskd3.infrastructure.database.base_db_service import BaseDBService

logger = logging.getLogger(__name__)

db = SQLAlchemy()


class SQLAlchemyDBService(BaseDBService):
    def __init__(self):
        self.db = db
        self.migrate = Migrate(db=self.db, directory="flaskd3/appcore/migrations")
        self.db_password_setter = None

    def setup_temp_db_password_reset(self, db_password_setter):
        self.db_password_setter = db_password_setter
        self.db_password_setter.init()

        @event.listens_for(Engine, "do_connect")
        def receive_do_connect(dialect, conn_rec, cargs, cparams):
            password = db_password_setter.reset_password()
            if password:
                cparams["passwd"] = password

    @staticmethod
    def log_query_profile(scope, perf_output):
        queries = get_debug_queries()
        profile_data = SQLAlchemyDBService._get_query_profile_data(queries)
        output_string = "-----------------------------------------------------------------------\n"
        output_string += "PATH: {}\n".format(scope)
        output_string += "TOTAL: %f ms QUERIES: %s\n" % (
            profile_data["total_duration"] * 1000,
            profile_data["no_of_queries"],
        )
        output_string += "SUMMARY:\n"
        output_string += "      HASH                        COUNT       TOTAL DURATION(ms)\n"
        for key, entry in profile_data["queries_summary"].items():
            output_string += "%s    %s      %.2f\n" % (
                key,
                entry["count"],
                entry["total_duration"] * 1000,
            )
        output_string += "DETAILS:\n"
        output_string += "      HASH                        DURATION(ms)     STATEMENT\n"
        for entry in profile_data["details"]:
            output_string += "%s    %.2f      %.100s\n" % (
                entry[0],
                entry[1] * 1000,
                entry[2],
            )
        output_string += "-----------------------------------------------------------------------"
        perf_output.write(output_string)

    @staticmethod
    def _get_query_profile_data(queries):
        db_profile_queries = list()
        queries_data = defaultdict(lambda: dict(count=0, total_duration=0))
        total_duration = 0
        for query in queries:
            hash_val = hashlib.md5(query.statement.encode()).hexdigest()
            data = queries_data[hash_val]
            data["count"] += 1
            data["total_duration"] += query.duration
            db_profile_queries.append([hash_val, query.duration, query.statement])
            total_duration += query.duration
        profile_data = dict(
            no_of_queries=len(queries),
            total_duration=total_duration,
            queries_summary=queries_data,
            details=db_profile_queries,
        )
        return profile_data

    def init(self, app, config, db_password_setter=None):
        if db_password_setter:
            self.setup_temp_db_password_reset(db_password_setter)
        db_config = DBConfig(config)
        if db_config.SSH_TUNNEL_CONFIG:
            import sshtunnel
            ssh_tunnel_config = json.loads(db_config.SSH_TUNNEL_CONFIG)
            tunnel = sshtunnel.SSHTunnelForwarder(
                ssh_address_or_host=(ssh_tunnel_config.get("ssh_host")),
                ssh_username=ssh_tunnel_config.get("ssh_username"), ssh_pkey=ssh_tunnel_config.get("ssh_pkey_file"),
                ssh_private_key_password=ssh_tunnel_config.get("ssh_pkey_passphrase"),
                remote_bind_address=(ssh_tunnel_config.get("remote_bind_address"), 3306)
            )
            tunnel.start()
            db_config.DB_MASTER_URL = "127.0.0.1"
            db_config.DB_PORT = tunnel.local_bind_port
        app.config["SQLALCHEMY_DATABASE_URI"] = db_config.get_url()
        self.db.init_app(app)
        self.migrate.init_app(app)

    def init_transaction(self):
        pass

    def commit(self):
        self.db.session.commit()

    def rollback(self):
        self.db.session.rollback()

    def get_db(self):
        return self.db
