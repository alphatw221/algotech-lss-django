
import pprint

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.utils.orm.campaign import *
from api.utils.orm.campaign_comment import *
from backend.api.facebook.page import *
from backend.api.facebook.post import *
from backend.api.facebook.user import *
from backend.campaign.campaign_comment.comment_processor import *
from backend.campaign.campaign_product.status_processor import \
    CampaignProductStatusProcessor
from backend.comment_catching.facebook.post_comment import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.campagin_product_test()

    def campagin_product_test(self):
        cp = CampaignProduct.objects.get(id=1)
        r = CampaignProductStatusProcessor.update_status(
            cp, CampaignProductStatusProcessor.Event.DEACTIVATE)

    def i18n_test(self):
        from backend.i18n.campaign_announcement import \
            i18n_get_campaign_announcement_lucky_draw_winner
        customer_name = 'John'
        product_name = 'Phone'
        print(i18n_get_campaign_announcement_lucky_draw_winner(
            customer_name, product_name))
        print(i18n_get_campaign_announcement_lucky_draw_winner(
            customer_name, product_name, lang='en'))
        print(i18n_get_campaign_announcement_lucky_draw_winner(
            customer_name, product_name, lang='zh-hant'))
        print(i18n_get_campaign_announcement_lucky_draw_winner(
            customer_name, product_name, lang='zh-hans'))
