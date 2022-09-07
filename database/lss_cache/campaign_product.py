import pottery 
from . import redis
KEY = 'campaign_products'

def __get_key(campaign_id):
    return f'{KEY}_{campaign_id}'

def get_campaign_products_map(campaign_id, plugin):
    if not redis.exists(f'{KEY}_{campaign_id}_{plugin}'):
        return None
    return pottery.RedisDict(redis=redis,key=f'{KEY}_{campaign_id}_{plugin}')

def leash_get_campaign_products_map(campaign_id, plugin):
    if redis.exists(f'{KEY}_{campaign_id}_{plugin}'):
        return True, pottery.RedisDict(redis=redis,key=f'{KEY}_{campaign_id}_{plugin}'), None

    campaign_product_map_lock = pottery.Redlock(key=f'{KEY}_{campaign_id}_{plugin}', masters={redis}, auto_release_time=5)
    return False, None, campaign_product_map_lock


def get_campaign_products(campaign_id):
    if not redis.exists(__get_key(campaign_id)):
        return None
    return pottery.RedisList(redis=redis,key=__get_key(campaign_id))

def leash_get_campaign_products(campaign_id):
    if redis.exists(__get_key(campaign_id)):
        return True, pottery.RedisList(redis=redis,key=__get_key(campaign_id)), None

    campaign_product_lock = pottery.Redlock(key=__get_key(campaign_id), masters={redis}, auto_release_time=5)
    return False, None, campaign_product_lock

def set_campaign_products(campaign_id, campaign_products):
    if redis.exists(__get_key(campaign_id)):
        redis.delete(__get_key(campaign_id))
    return pottery.RedisList(campaign_products, redis=redis, key=__get_key(campaign_id))

def invalidate(campaign_id):
    redis.delete(__get_key(campaign_id))