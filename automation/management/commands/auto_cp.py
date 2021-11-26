import pendulum
from automation.utils.timeloop import time_loop
from backend.campaign.campaign.manager import CampaignManager
from backend.campaign.campaign_comment.comment_processor import \
    CommentProcessor
from django.conf import settings
from django.core.management.base import BaseCommand


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

        for campaign in CampaignManager.get_ordering_campaigns():
            try:
                result = CommentProcessor(
                    campaign,
                    comment_batch_size=settings.COMMENT_PROCESSING['COMMENT_BATCH_SIZE'],
                    max_response_workers=settings.COMMENT_PROCESSING['MAX_RESPONSE_WORKERS'],
                    enable_order_code=True,
                    only_activated_order_code=False,
                    response_platforms=['facebook', 'youtube']
                ).process()
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                result = e
            print(f'{pendulum.now()} - {campaign.title=} {campaign.id=} - {result=}')
