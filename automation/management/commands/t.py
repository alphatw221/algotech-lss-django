
import pprint

from api.models.campaign.campaign import Campaign
from api.utils.orm.campaign import *
from api.utils.orm.campaign_comment import *
from backend.api.facebook.page import *
from backend.api.facebook.post import *
from backend.api.facebook.user import *
from backend.campaign.campaign_comment.comment_processor import *
from backend.comment_catching.facebook.post_comment import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.i18n_test()

    def i18n_test(self):
        from backend.i18n._sample import i18n_sample
        items = [('AAA', 1), ('BBB', 10)]
        print(i18n_sample(items, lang='en'))
        print(i18n_sample(items, lang='zh-hant'))
        print(i18n_sample(items, lang='zh-hans'))
