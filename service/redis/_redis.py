from django.conf import settings
from rq import Queue
from redis import Redis

redis_info=settings.REDIS_SERVER
redis_connection=Redis(host=redis_info['host'],port=redis_info['port'],password=redis_info['password'])