from django.core.management.base import BaseCommand

from automation.utils.timeloop import time_loop
from api import models
import pendulum
import service
import lib


# from backend.google_cloud_monitoring.google_cloud_monitoring import CommentQueueLengthMetric


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.scan_live_campaign()

    @time_loop(10)
    def scan_live_campaign(self):
        
        self.stdout.write(self.style.SUCCESS(
            f'{pendulum.now()} - scan_live_campaign Module'))

        # CommentQueueLengthMetric.write_time_series(len(comment_queue.jobs))
        rows=[]
        for campaign in models.campaign.campaign.Campaign.objects.filter(start_at__lt=pendulum.now(),end_at__gt=pendulum.now()):
            if not service.rq.job.exists(campaign.id):
                service.rq.job.enqueue_campaign_job(campaign.id)
                rows.append([campaign.id, ""])
                continue

            job, job_status = service.rq.job.get_job_status(campaign.id)
            rows.append([campaign.id, job_status])
            if job_status == 'queued':
                count = service.redis.redis.get_count()(campaign.id)
                if count >5:
                    job.delete()
                    service.redis.redis.delete(campaign.id)
                else:
                    service.redis.redis.increment(campaign.id)
            elif job_status in ('started', 'deferred'):
                # job.delete()
                continue
            elif job_status in ('finished', 'failed', 'canceled'):  #
                job.delete()
                service.redis.redis.delete(campaign.id)
                service.rq.job.enqueue_campaign_job(campaign.id)

        lib.util.logger.print_table(["Campaign ID", "Status"],rows)