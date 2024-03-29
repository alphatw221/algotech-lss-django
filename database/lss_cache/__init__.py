from redis import Redis
from django.conf import settings
import pottery

AUTO_RELEASE_TIME = 2

redis=Redis(host=settings.CACHE_SERVER['host'],port=settings.CACHE_SERVER['port'],password=settings.CACHE_SERVER['password'])

def get_key(base_key, *args):
    key = base_key
    for arg in args:
        key+=f'_{arg}'
    return key


# def _set_dict(key, data):
#     if redis.exists(key):
#         redis.delete(key)
#     return pottery.RedisDict(data, redis=redis, key=key)

# def _set_list(key, data):
#     if redis.exists(key):
#         redis.delete(key)
#     return pottery.RedisList(data, redis=redis, key=key)

# def _leash_get_dict(key):
#     try:
#         if not redis.exists(key):
#             redis_lock = pottery.Redlock(key=key, masters={redis}, auto_release_time=AUTO_RELEASE_TIME)
#             return False, None, redis_lock
#         data = dict(pottery.RedisDict(redis=redis,key=key))
#         return True, data, None
#     except Exception:
#         return False, None, None



# def _leash_get_list(key):
#     try:
#         if not redis.exists(key):
#             redis_lock = pottery.Redlock(key=key, masters={redis}, auto_release_time=AUTO_RELEASE_TIME)
#             return False, None, redis_lock
#         pottery_list = pottery.RedisList(redis=redis,key=key)
#         print(pottery_list)
#         data = list(pottery_list)
#         return True, data, None
#     except Exception:
#         return False, None, None


# @pottery.redis_cache(redis=redis, key='test')
# def _query_with_cache(collection, key=None, **kwargs):
#     import time
#     print(key)
#     print(collection.filter(**kwargs))
#     time.sleep(5)
#     return 2
#     # return collection.filter(**kwargs)

from . import campaign_product