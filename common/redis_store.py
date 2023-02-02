import os

import redis

# 这个地方的host地址依赖docker中运行时的环境变量，如果不是docker运行，需要自己修改
pool = redis.ConnectionPool(host=os.environ.get('REDIS_HOST'), port=6379, password='rdspwd123456!', db=0, decode_responses=True)
redis_store = redis.Redis(connection_pool=pool, decode_responses=True)


def redis_store_get(key):
    if _value := redis_store.get(key):
        return _value
    else:
        raise KeyError


def redis_store_set(key, value):
    return redis_store.set(key, value)
