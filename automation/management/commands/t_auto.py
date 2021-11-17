import threading
import time
import traceback
import pendulum
from django.core.management.base import BaseCommand
from api.models.campaign.campaign import Campaign
from api.utils.common.facebook.post_comment import FacebookCaptureCommentError, campaign_facebook_post_capture_comments
from django.conf import settings


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # threading.Thread(target=print_now, daemon=True).start()
        # waiting_for_SIGINT = threading.Event().wait()
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


@time_loop(5)
def print_now():
    print(pendulum.now())


@time_loop(settings.FACEBOOK_COMMENT_CAPTURING['REST_INTERVAL_SECONDS'])
def campaign_facebook_capture_comments():
    for campaign in Campaign.objects.all():
        try:
            result = campaign_facebook_post_capture_comments(campaign)
        except Exception as e:
            result = e
        print(f'{pendulum.now()} - {campaign.title=} {campaign.id=} - {result=}')
