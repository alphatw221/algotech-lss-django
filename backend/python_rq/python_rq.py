import redis
from rq import Queue
from redis import Redis
from datetime import datetime, timedelta

# redis_connection=Redis()
# q=Queue(name='queue_name',connection=redis_connection)



# def capture_and_process():
#     pass
#     q.enqueue_in(timedelta(seconds=5),capture_and_process)

# q.enqueue_in(timedelta(seconds=5),capture_and_process)