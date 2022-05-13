from ._redis import redis_connection


def increment(key):
    count = redis_connection.get(key) if redis_connection.get(key) else 0
    return redis_connection.set(key, count+1)

def set(key, value):
    return redis_connection.set(key, value)

def get(key):
    return redis_connection.get(key)

def get_count(key):
    return redis_connection.get(key) if redis_connection.get(key) else 0
    
def delete(key):
    return redis_connection.delete(key)