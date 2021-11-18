from django.core.management.base import BaseCommand
from api.models.campaign.campaign import Campaign
from api.utils.api.facebook.page import *
from api.utils.api.facebook.user import *
from api.utils.api.facebook.post import *
from backend.utils.campaign_comment.comment_processor import *
from backend.utils.facebook.post_comment import *
from api.utils.orm.campaign import *
from api.utils.orm.campaign_comment import *
import pprint


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        campaign = Campaign.objects.get(pk=2)
        processor = CommentProcessor(campaign)
        processor.process()
