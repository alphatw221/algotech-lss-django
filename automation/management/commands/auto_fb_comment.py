import time
import traceback
import pendulum
from django.core.management.base import BaseCommand
from api.utils.orm.campaign import get_active_campaign_now
from api.utils.common.facebook.post_comment import campaign_facebook_post_capture_comments
from django.conf import settings


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        campaign_facebook_capture_comments()


def time_loop(sleep_time):
    def decorator(func):
        def wrapper(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except Exception:
                    print(traceback.format_exc())
                time.sleep(sleep_time)
        return wrapper
    return decorator


@time_loop(settings.FACEBOOK_COMMENT_CAPTURING['REST_INTERVAL_SECONDS'])
def campaign_facebook_capture_comments():
    print(f'{pendulum.now()} - Auto Facebook Comment Module')
    for campaign in get_active_campaign_now():
        try:
            result = campaign_facebook_post_capture_comments(campaign)
        except Exception as e:
            result = e
        print(f'  {pendulum.now()} - {campaign.title=} {campaign.id=} - {result=}')
