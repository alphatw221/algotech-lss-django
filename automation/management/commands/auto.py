from django.conf import settings
import pendulum
from automation.utils.timeloop import time_loop
from backend.campaign.campaign.manager import CampaignManager
from django.core.management.base import BaseCommand
from backend.python_rq.python_rq import redis_connection, campaign_queue, comment_queue
from rq.job import Job
from automation.jobs.campaign_job import campaign_job

from datetime import datetime
from backend.pymongo.mongodb import db,client

from backend.google_cloud_monitoring.google_cloud_monitoring import CommentQueueLengthMetric

class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.scan_live_campaign()

    @time_loop(settings.FACEBOOK_COMMENT_CAPTURING['REST_INTERVAL_SECONDS'])
    def scan_live_campaign(self):
        self.stdout.write(self.style.SUCCESS(
            f'{pendulum.now()} - scan_live_campaign Module'))

        CommentQueueLengthMetric.write_time_series(len(comment_queue.jobs))
        for campaign in CampaignManager.get_ordering_campaigns():
            try:
                print(campaign.id)
                if not Job.exists(str(campaign.id),connection=redis_connection):
                    campaign_queue.enqueue(campaign_job,job_id=str(campaign.id),args=(campaign.id,), result_ttl=10, failure_ttl=10)
                    continue

                job = Job.fetch(str(campaign.id), connection=redis_connection)
                job_status=job.get_status(refresh=True)
                print(job_status)
                if  job_status in ('queued','started','deferred'):
                    continue
                    # job.delete()
                elif job_status in ('finished','failed'):
                    job.delete()
                    campaign_queue.enqueue(campaign_job,job_id=str(campaign.id),args=(campaign.id,), result_ttl=10, failure_ttl=10)

            except Exception as e:
                print(e)








