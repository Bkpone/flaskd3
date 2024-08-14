EXTERNAL_CLIENTS_LOGGER_PREFIX = "external_clients_"
HASH_PRECISION = 11  # precison for python geohash lib, match redis GEOHASH
UNITS = ["km", "m", "mi", "ft"]


class StatusCode(object):
    # Success
    SUCCESS = 200

    # Client Error
    BAD_REQUEST = 400

    # Server Error
    SERVER_ERROR = 500

    # prevent set
    def __setattr__(self, *_):
        pass
