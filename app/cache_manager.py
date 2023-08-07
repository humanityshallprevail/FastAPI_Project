import logging

import redis  # type: ignore[import]

from config import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)


def get_from_cache(key):
    value = r.get(key)
    logging.debug(f'Getting from cache for key {key}: {value}')
    return value


def set_in_cache(key, value, expiration_time=3600):
    logging.debug(f'Setting cache for key {key}: {value}')
    r.setex(key, expiration_time, value)


def invalidate_cache(key):
    r.delete(key)
