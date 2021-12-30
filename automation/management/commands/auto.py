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


class DBException(Exception):
    """Error when capturing Facebook comments."""
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

        for campaign in CampaignManager.get_ordering_campaigns():
            try:
                print(campaign.id)
                if not Job.exists(str(campaign.id),connection=redis_connection):
                    campaign_queue.enqueue(campaign_job,job_id=str(campaign.id),args=(campaign.id,))
                    continue

                job = Job.fetch(str(campaign.id), connection=redis_connection)
                job_status=job.get_status(refresh=True)
                print(job_status)
                if  job_status in ('queued','started','deferred'):
                    continue
                elif job_status in ('finished','failed'):
                    job.delete()
                    campaign_queue.enqueue(campaign_job,job_id=str(campaign.id),args=(campaign.id,))

            except DBException as e:
                print(e)
            # except Exception as e:
            #     print(e)









