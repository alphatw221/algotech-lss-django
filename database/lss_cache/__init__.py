from redis import Redis
from django.conf import settings


redis=Redis(host=settings.CACHE_SERVER['host'],port=settings.CACHE_SERVER['port'],password=settings.CACHE_SERVER['password'])

from . import campaign_product