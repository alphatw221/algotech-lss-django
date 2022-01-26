import pprint

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.cart.cart_product import CartProduct
from api.utils.orm import campaign_comment, cart_product
from backend.api.facebook.page import *
from backend.api.facebook.post import *
from backend.api.facebook.user import *
from backend.campaign.campaign.manager import CampaignManager
# from backend.campaign.campaign_comment.comment_processor import *
from backend.campaign.campaign_lucky_draw.event import (
    DrawFromCampaignCommentsEvent, DrawFromCampaignLikesEvent,
    DrawFromCartProductsEvent)
from backend.campaign.campaign_lucky_draw.manager import \
    CampaignLuckyDrawManager
from backend.campaign.campaign_product.status_processor import \
    CampaignProductStatusProcessor
from backend.cart.cart.manager import CartManager
from backend.cart.cart_product.request import CartProductRequest
from backend.comment_catching.facebook.post_comment import *
from django.core.management.base import BaseCommand
from api.views.order.order_report import *
from backend.pymongo.mongodb import db
from api.models.youtube.youtube_channel import YoutubeChannel
from automation.jobs.campaign_job import *

from backend.api.youtube.viedo import api_youtube_get_video_info
from automation.jobs.campaign_job import campaign_job
class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # self.lucky_draw_test()
        # from backend.google_cloud_monitoring.google_cloud_monitoring import CommentQueueLengthMetric
        # CommentQueueLengthMetric.create_metric_descriptor()
        # CommentQueueLengthMetric.write_time_series(10)
        # CommentQueueLengthMetric.delete_metric_descriptor()
        self.campaign_test()
        # self.ipg_test()
        # self.youtube_test()

    def campaign_test(self):
        cs = CampaignManager.get_active_campaigns()
        print(cs)
        cs = CampaignManager.get_ordering_campaigns()
        print(cs)

    def cart_product_manager_test(self):
        campaign = Campaign.objects.get(id=1)
        campaign_product = CampaignProduct.objects.get(id=1)

        cart_product_request = CartManager.create_cart_product_request(
            campaign, 'facebook', '3141324909312956', 'Liu Ian', {
                campaign_product: 5,
            }
        )
        cart_product_request = CartManager.process(cart_product_request)

    def lucky_draw_test(self):
        c = Campaign.objects.get(id=1)
        cp = CampaignProduct.objects.get(id=1)
        prize_cp = CampaignProduct.objects.get(id=2)

        # lucky_draw = CampaignLuckyDrawManager.process(
        #     c, DrawFromCampaignLikesEvent(c), prize_cp, 1,
        # )

        # keyword='testtest'
        # lucky_draw = CampaignLuckyDrawManager.process(
        #     c, DrawFromCampaignCommentsEvent(c, keyword), prize_cp, 1,
        # )

        lucky_draw = CampaignLuckyDrawManager.process(
            c, DrawFromCartProductsEvent(c, cp), prize_cp, 1,
        )

        print(lucky_draw.__dict__)

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


    def ipg_test(self):
        from api.views.payment._payment import IPG_Helper
        chargetotal=10
        currency='702'
        timezone = "Asia/Singapore"
        IPG_Helper.create_payment(timezone, chargetotal, currency)

    def youtube_test(self):
        ret, code = api_youtube_get_video_info("5qap5aO4i9A")

        print(f"code :{code}")
        print(f"ret :{ret}")

    def campaign_test(self):
        campaign_job(53)
# $stringToHash = $this->storeId . $this->txndatetime . $this->chargetotal . $this->currency . $this->sharedSecret;
#         $ascii = bin2hex($stringToHash);

#         return hash("sha256", $ascii);