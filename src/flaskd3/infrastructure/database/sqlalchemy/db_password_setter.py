from flask import current_app
from flaskd3.common.utils.dateutils import current_datetime


class BaseDbPasswordSetter:
    def __init__(self, reset_interval, db_config):
        self.reset_interval = reset_interval
        self.last_reset_time = current_datetime()
        self.db_config = db_config

    def init(self):
        self.last_reset_time = current_datetime()

    def reset_password(self):
        timedelta = current_datetime() - self.last_reset_time
        if timedelta.total_seconds() > self.reset_interval:
            self.last_reset_time = current_datetime()
            self.db_config.set_password = self._generate_password()
            current_app.config["SQLALCHEMY_DATABASE_URI"] = self.db_config.get_url()
            return self.db_config.password
        return None

    def _generate_password(self):
        raise NotImplementedError("Function to be implemented by a specific implementation")
