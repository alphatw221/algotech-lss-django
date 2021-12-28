from django.conf import settings
import pendulum
from automation.utils.timeloop import time_loop
from backend.campaign.campaign.manager import CampaignManager
from django.core.management.base import BaseCommand
from backend.python_rq.python_rq import redis_connection, campaign_queue
from rq.job import Job
from automation.jobs.campaign_job import campaign_job

from datetime import datetime
from backend.pymongo.mongodb import db,client

class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # self.campaign_facebook_capture_comments()
        self.scan_live_campaign()

    @time_loop(settings.FACEBOOK_COMMENT_CAPTURING['REST_INTERVAL_SECONDS'])
    def scan_live_campaign(self):
        self.stdout.write(self.style.SUCCESS(
            f'{pendulum.now()} - scan_live_campaign Module'))

        for campaign in CampaignManager.get_ordering_campaigns():
            try:
                job = Job.fetch(campaign.id, connection=redis_connection)
                if not job:
                    campaign_queue.enqueue(campaign_job,job_id=campaign.id,args=(campaign.id,))
                    continue
                job_status=job.get_status(refresh=True)
                if  job_status in ('queued','started','deferred'):
                    continue
                elif job_status in ('finished','failed'):
                    job.delete()
                    campaign_queue.enqueue(campaign_job,job_id=campaign.id,args=(campaign.id,))


            except Exception as e:
                print(e)









