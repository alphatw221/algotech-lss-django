from datetime import datetime
from django.core.management.base import BaseCommand

import pendulum
import service
from automation import jobs

# from backend.google_cloud_monitoring.google_cloud_monitoring import CommentQueueLengthMetric


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.renew_facebook_cookies()

    def renew_facebook_cookies(self):
        
        self.stdout.write(self.style.SUCCESS(
            f'{pendulum.now()} - starting renew_facebook_cookies crawler'))
        crawler = service.web_crawler.renew_facebook_cookies_crawler.RenewFacebookCookiesCrawler()
        crawler.start()
        