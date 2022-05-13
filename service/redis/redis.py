from ._redis import redis_connection


def increment(key):
    return redis_connection.set(key, redis_connection.get(key)+1)

def set(key, value):
    return redis_connection.set(key, value)

def get(key):
    return redis_connection.get(key)

def delete(key):
    return redis_connection.delete(key)