import pendulum
from django.conf import settings
from django.core.management.base import BaseCommand
from api.utils.common.campaign_comment.comment_processor import CommentProcessor
from automation.utils.timeloop import time_loop
from api.utils.orm.campaign import get_active_campaign_now


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.campaign_comments_processing()

    @time_loop(settings.COMMENT_PROCESSING['REST_INTERVAL_SECONDS'])
    def campaign_comments_processing(self):
        self.stdout.write(self.style.SUCCESS(
            f'{pendulum.now()} - Auto Campaign Comments Module'))

        for campaign in get_active_campaign_now():
            try:
                processor = CommentProcessor(campaign)
                result = processor.process()
            except Exception as e:
                result = e
            print(f'{pendulum.now()} - {campaign.title=} {campaign.id=} - {result=}')
