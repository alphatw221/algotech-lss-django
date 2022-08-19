from django.conf import settings
from rq import Queue
from redis import Redis

redis_info=settings.REDIS_SERVER
redis_connection=Redis(host=redis_info['host'],port=redis_info['port'],password=redis_info['password'])

campaign_queue=Queue(name='campaign_queue',connection=redis_connection)
comment_queue=Queue(name='comment_queue',connection=redis_connection)
email_queue=Queue(name='email_queue', connection=redis_connection)
report_queue=Queue(name='report_queue',connection=redis_connection)
general_queue=Queue(name='general_queue',connection=redis_connection)
test_queue=Queue(name='test_queue',connection=redis_connection)
