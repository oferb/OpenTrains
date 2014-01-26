import redis

CLIENT = redis.StrictRedis()

def get_client():
    return CLIENT

