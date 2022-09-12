import pottery

from api.models import campaign 
from . import redis, get_key
KEY = 'campaign_products'

DATA_EXTERNAL_INTERNAL_MAP = 'external_internal_map'
DATA_INTERNAL_EXTERNAL_MAP = 'internal_external_map'

AUTO_RELEASE_TIME = 2

def leash_get_external_internal_map(campaign_id, plugin):
    try:
        key = get_key(KEY, campaign_id, plugin, DATA_EXTERNAL_INTERNAL_MAP)
        print(key)
        data = dict(pottery.RedisDict(redis=redis,key=key))
        if not data:
            campaign_product_map_lock = pottery.Redlock(key=key, masters={redis}, auto_release_time=AUTO_RELEASE_TIME)
            return False, None, campaign_product_map_lock
        return True, data, None
    except Exception:
        return False, None, None
        
def set_external_internal_map(campaign_id, plugin, external_internal_map):
    key = get_key(KEY, campaign_id, plugin, DATA_EXTERNAL_INTERNAL_MAP)
    print(key)
    if redis.exists(key):
        redis.delete(key)
    return pottery.RedisDict(external_internal_map, redis=redis, key=key)

def leash_get_internal_external_map(campaign_id, plugin):
    try:
        key = get_key(KEY, campaign_id, plugin, DATA_INTERNAL_EXTERNAL_MAP)
        data = dict(pottery.RedisDict(redis=redis,key=key))
        if not data:
            campaign_product_map_lock = pottery.Redlock(key=key, masters={redis}, auto_release_time=AUTO_RELEASE_TIME)
            return False, None, campaign_product_map_lock
        return True, data, None
    except Exception:
        return False, None, None

def set_internal_external_map(campaign_id, plugin, internal_external_map):
    key = get_key(KEY, campaign_id, plugin, DATA_INTERNAL_EXTERNAL_MAP)
    if redis.exists(key):
        redis.delete(key)
    return pottery.RedisDict(internal_external_map, redis=redis, key=key)






def get(campaign_id):
    if not redis.exists(get_key(KEY,campaign_id)):
        return None
    return pottery.RedisList(redis=redis,key=get_key(KEY,campaign_id))

def leash_get(campaign_id):
    if redis.exists(get_key(KEY,campaign_id)):
        return True, pottery.RedisList(redis=redis,key=get_key(KEY,campaign_id)), None

    campaign_product_lock = pottery.Redlock(key=get_key(KEY,campaign_id), masters={redis}, auto_release_time=5)
    return False, None, campaign_product_lock

def set(campaign_id, campaign_products):
    if redis.exists(get_key(KEY,campaign_id)):
        redis.delete(get_key(KEY,campaign_id))
    return pottery.RedisList(campaign_products, redis=redis, key=get_key(KEY,campaign_id))


def invalidate(*args):
    key = get_key(KEY,*args)
    print(key)
    redis.delete(key)