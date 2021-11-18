import pendulum
from django.conf import settings
from django.core.management.base import BaseCommand
from automation.utils.timeloop import time_loop
from api.utils.orm.campaign import get_active_campaign_now
from api.utils.common.facebook.post_comment import campaign_facebook_post_capture_comments


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

        for campaign in get_active_campaign_now():
            try:
                result = campaign_facebook_post_capture_comments(campaign)
            except Exception as e:
                result = e
            print(f'{pendulum.now()} - {campaign.title=} {campaign.id=} - {result=}')