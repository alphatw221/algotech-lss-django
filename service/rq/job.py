from ._rq import redis_connection,campaign_queue
from rq.job import Job
from automation import jobs

def exists(job_id):
    return Job.exists(str(job_id), connection=redis_connection)

def enqueue_campaign_job(campaign_id):
    campaign_queue.enqueue(jobs.campaign_job.campaign_job, job_id=str(campaign_id), args=(
                    campaign_id,), result_ttl=10, failure_ttl=10)


def get_job_status(job_id):
    job = Job.fetch(str(job_id), connection=redis_connection)
    return job, job.get_status(refresh=True)