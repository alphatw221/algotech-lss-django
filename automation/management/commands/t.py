
from django.core.management.base import BaseCommand
from api.models.campaign.campaign import Campaign
from backend.utils.api.facebook.page import *
from backend.utils.api.facebook.user import *
from backend.utils.api.facebook.post import *
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
        self.i18n()

    def i18n(self):
        from backend.i18n.product_added import i18n_product_added
        items = [('AAA', 1), ('BBB', 10)]
        print(i18n_product_added(items, lang='en'))
        print(i18n_product_added(items, lang='zh-hant'))
