from rq import Queue
from redis import Redis
from django.conf import settings

redis_info=settings.REDIS_SERVER
redis_connection=Redis(host=redis_info['host'],port=redis_info['port'],password=redis_info['password'])

campaign_queue=Queue(name='campaign_queue',connection=redis_connection)
comment_queue=Queue(name='comment_queue',connection=redis_connection)

