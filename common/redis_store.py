import redis

pool = redis.ConnectionPool(host='123.123.123.123', port=6379, password='password', db=0, decode_responses=True)
redis_store = redis.Redis(connection_pool=pool, decode_responses=True)


def redis_store_get(key):
    if _value := redis_store.get(key):
        return _value
    else:
        raise KeyError


def redis_store_set(key, value):
    return redis_store.set(key, value)
