from ._rq import redis_connection
from rq.job import Job

def exists(job_id):
    return Job.exists(str(job_id), connection=redis_connection)


def get_job_status(job_id):
    job = Job.fetch(str(job_id), connection=redis_connection)
    return job, job.get_status(refresh=True)