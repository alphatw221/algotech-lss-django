from datetime import datetime
from django.core.management.base import BaseCommand

from automation.utils.timeloop import time_loop
from api import models
import pendulum
import service
import lib
from automation import jobs



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
        for campaign in models.campaign.campaign.Campaign.objects.filter(user_subscription__isnull=False, start_at__lt=datetime.utcnow(),end_at__gt=datetime.utcnow()):
            invalid_facebook = not campaign.facebook_campaign.get("post_id", None)
            invalid_instagram = not campaign.instagram_campaign.get("live_media_id", None)
            invalid_youtube = not campaign.youtube_campaign.get("live_video_id", None)
            invalid_twitch = not campaign.twitch_campaign.get("channel_name", None)
            invalid_tiktok = not campaign.tiktok_campaign.get("username", None)
            if invalid_facebook and invalid_instagram and invalid_youtube and invalid_twitch and invalid_tiktok:
                continue
            if not service.rq.job.exists(campaign.id):
                service.rq.queue.enqueue_unique_job_to_campaign_queue(jobs.campaign_job.campaign_job, campaign_id = campaign.id)
                rows.append([campaign.id, ""])
                continue

            job, job_status = service.rq.job.get_job_status(campaign.id)
            rows.append([campaign.id, job_status])
            if job_status == 'queued':
                count = service.redis.redis.get_count(campaign.id)
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
                service.rq.queue.enqueue_unique_job_to_campaign_queue(jobs.campaign_job.campaign_job, campaign_id = campaign.id)

        lib.util.logger.print_table(["Campaign ID", "Status"],rows)