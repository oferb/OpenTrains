import redis

_CLIENT = redis.StrictRedis()

def get_redis_client():
    return _CLIENT

def get_redis_pipeline():
    return _CLIENT.pipeline()

