import json
import logging

from flaskd3.infrastructure.database.redis.redis_repository import RedisRepository
from flaskd3.common.value_objects import GeoLocation

logger = logging.getLogger(__name__)


class GeoRedisRepository(RedisRepository):
    def _set_data_as_json(self, key, data):
        """
        Store data using Redis's set() as json dumps
        """
        return self.set(key, json.dumps(data))

    def save_location_data(self, scope, geo_location, item_id):
        self.store.geoadd(scope, geo_location.longitude, geo_location.latitude, item_id)

    def load_by_radius(self, scope, geo_location, radius, with_dist):
        """
        Return list of locations in redis in a radius from original lat, lon.
        Data return: lat, lon, distance to original, additional data
        """
        distance_data = self.store.georadius(
            scope,
            geo_location.longitude_float,
            geo_location.latitude_float,
            radius.value,
            radius.unit.value,
            with_dist,
        )
        return distance_data

    def load_all(self, scope):
        """
        Return all locations in redis, with lat, lon, additional data
        """
        names = self.store.zrange(scope, 0, -1)
        data = []
        lat_longs = self.redis_store.geopos(scope, names)
        for i, name in enumerate(names):
            data_location = dict(
                item_id=name,
                geo_location=GeoLocation(longitude=lat_longs[i][0], latitude=lat_longs[i][1]),
            )
            data.append(data_location)
        return data

    def delete_location_data(self, scope, item_id):
        """
        Remove location from redis
        (1) remove data from delete(name)
        (2) remove to sorted set using zrem(key, name)
        """
        try:
            self.store.zrem(scope, item_id)
        except Exception:
            logger.exception("Unable to delete from redis: {}:{}".format(scope, item_id))
            return False
        return True
