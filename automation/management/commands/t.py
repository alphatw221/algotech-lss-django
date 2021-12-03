
import pprint

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.cart.cart_product import CartProduct
from api.utils.orm import campaign_comment, cart_product
from backend.api.facebook.page import *
from backend.api.facebook.post import *
from backend.api.facebook.user import *
from backend.campaign.campaign.manager import CampaignManager
from backend.campaign.campaign_comment.comment_processor import *
from backend.campaign.campaign_lucky_draw.event import (
    DrawFromCampaignCommentsEvent, DrawFromCartProductsEvent)
from backend.campaign.campaign_lucky_draw.manager import \
    CampaignLuckyDrawManager
from backend.campaign.campaign_product.status_processor import \
    CampaignProductStatusProcessor
from backend.comment_catching.facebook.post_comment import *
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.lucky_draw_test()

    def campaign_test(self):
        cs = CampaignManager.get_active_campaigns()
        print(cs)
        cs = CampaignManager.get_ordering_campaigns()
        print(cs)

    def lucky_draw_test(self):
        c = Campaign.objects.get(id=1)
        cp = CampaignProduct.objects.get(id=1)

        # lucky_draw = CampaignLuckyDrawManager.process(
        #     c, DrawFromCampaignCommentsEvent(c, 'hi'), cp, 1,
        # )
        # print(lucky_draw)

        # lucky_draw = CampaignLuckyDrawManager.process(
        #     c, DrawFromCartProductsEvent(c, cp), cp, 10,
        # )
        # print(lucky_draw)

    def cart_product_test(self):
        c = Campaign.objects.get(id=1)
        cp = CampaignProduct.objects.get(id=1)
        cps = cart_product.filter_cart_products(
            c, cp, ('order_code', 'cart'), ('valid',))
        print(c, cp, cps)

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
