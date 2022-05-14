from ._rq import redis_connection,campaign_queue,comment_queue
from rq.job import Job

def exists(job_id):
    return Job.exists(str(job_id), connection=redis_connection)

def enqueue_campaign_queue(job, campaign_id):
    campaign_queue.enqueue(job, job_id=str(campaign_id), args=(
                    campaign_id,), result_ttl=10, failure_ttl=10)

def enqueue_comment_queue(job,campaign, platform_name, platform, uni_format_comment, order_codes_mapping):
    comment_queue.enqueue(job, args=(campaign, platform_name, platform,
                                  uni_format_comment, order_codes_mapping), result_ttl=10, failure_ttl=10)
    pass
def get_job_status(job_id):
    job = Job.fetch(str(job_id), connection=redis_connection)
    return job, job.get_status(refresh=True)