from datetime import datetime
import pendulum
from api.models.campaign.campaign_comment import CampaignComment
from automation.utils.timeloop import time_loop
from backend.campaign.campaign.manager import CampaignManager
from backend.campaign.campaign_product.manager import CampaignProductManager
from backend.comment_catching.facebook.post_comment import \
    campaign_facebook_post_capture_comments
from django.conf import settings
from django.core.management.base import BaseCommand
from backend.pymongo.mongodb import db,client
from backend.python_rq.python_rq import redis_connection, campaign_queue, comment_queue

from api.models.campaign.campaign import Campaign
from api.utils.orm.campaign_comment import (get_comments_count,
                                            get_latest_commented_at,
                                            update_or_create_comment)
from backend.api.facebook.post import api_fb_get_post_comments
from django.conf import settings
from rq.job import Job
from backend.campaign.campaign_comment.comment_processor import RQCommentProcessor

class FacebookCaptureCommentError(Exception):
    """Error when capturing Facebook comments."""

class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.campaign_facebook_capture_comments()

    @time_loop(settings.FACEBOOK_COMMENT_CAPTURING['REST_INTERVAL_SECONDS'])
    def campaign_facebook_capture_comments(self):
        self.stdout.write(self.style.SUCCESS(
            f'{pendulum.now()} - Auto Facebook Comment Module'))

        for campaign in CampaignManager.get_ordering_campaigns():
            try:
                result = campaign_facebook_post_capture_comments(campaign)
            except Exception as e:
                result = e
            print(f'{pendulum.now()} - {campaign.title=} {campaign.id=} - {result=}')
