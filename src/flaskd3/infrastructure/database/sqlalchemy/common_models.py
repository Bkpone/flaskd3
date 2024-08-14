import pytz  # from PyPI
from sqlalchemy import types as types

from flaskd3.common.utils import dateutils


class AwareDateTime(types.TypeDecorator):
    """
    Results returned as aware datetimes, not naive ones.
    """

    impl = types.TIMESTAMP
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return dateutils.datetime_to_utc(value) if value else value

    def process_result_value(self, value, dialect):
        return value.replace(tzinfo=pytz.utc) if value else value

