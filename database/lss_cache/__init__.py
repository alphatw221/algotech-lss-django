from redis import Redis
from django.conf import settings


redis=Redis(host=settings.CACHE_SERVER['host'],port=settings.CACHE_SERVER['port'],password=settings.CACHE_SERVER['password'])

def get_key(base_key, *args):
    key = base_key
    for arg in args:
        key+=f'_{arg}'
    return key


from . import campaign_product