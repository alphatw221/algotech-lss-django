from ._redis import redis_connection


def increment(key):
    byte = redis_connection.get(key)
    count = int(byte) if byte else 0
    return redis_connection.set(key, str(count+1))

def set(key, value):
    return redis_connection.set(key, value)

def set_count(key, count):
    return redis_connection.set(key, str(count))

def get(key):
    return redis_connection.get(key)

def get_count(key):
    byte = redis_connection.get(key)
    return int(byte) if byte else 0

def delete(key):
    return redis_connection.delete(key)