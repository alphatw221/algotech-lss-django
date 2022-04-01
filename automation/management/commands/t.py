import imp
import pprint
import requests


from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.cart.cart_product import CartProduct
from api.models.user.user import User
from api.models.user.user_subscription import UserSubscription
from api.utils.orm import campaign_comment, cart_product
from backend.api.google.user import api_google_get_userinfo
from backend.api.youtube.channel import api_youtube_get_list_channel_by_token
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
from django.core.management.base import BaseCommand
from backend.pymongo.mongodb import db, get_incremented_filed
from automation.jobs.campaign_job import campaign_job
from django.conf import settings

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.product.product import Product
from api.models.order.order import Order
from api.models.order.order_product import OrderProduct
import datetime
from backend.api.instagram.post import api_ig_post_comment_on_media, api_ig_get_post_comments


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.test_mongodb_query()
        # self.add_user_subscription_user()
        # self.lucky_draw_test()
        # from backend.google_cloud_monitoring.google_cloud_monitoring import CommentQueueLengthMetric
        # CommentQueueLengthMetric.create_metric_descriptor()
        # CommentQueueLengthMetric.write_time_series(10)
        # CommentQueueLengthMetric.delete_metric_descriptor()

        # self.convert_arimme()

        # campaign_job(111)
        # ret = api_youtube_get_video_comment_thread('', 'xATwFaLCrKM', 5)
        # print (ret)
        
        # self.campaign_test()
        # self.ipg_test()
        # self.youtube_test()
        # campaign_job(109)
        # send_email(273)
        # code,data = api_google_post_refresh_token("1//0eEcTGHyIHZidCgYIARAAGA4SNwF-L9IrBxG90zwkR-Y7k4QoYBjY5H8JjykXbHi1QvqbVdaZPNejuNpkcxc8wjVIixgC_UKgCeQ")
        # print(code)
        # print(data)

        # from dataclasses import dataclass
        # from backend.api._api_caller import RestApiJsonCaller
        # class Laravel_Helper:
        #     @dataclass
        #     class LaravelApiCaller(RestApiJsonCaller):
        #         domain_url: str = "https://v1login.liveshowseller.com/api/ig_private_msg"
        
        # data = {
        #     "accessToken": "EAANwBngXqOABAOy6CE0qFi92dImqOwDIWzvNzyvD0PNsLt0WqUIJiwNzZBbLvkEb1s1SlRUZAIPiI4Pw143KFiTfkbozmDnzZCrTY5Dj4J30qHVvVJejIyeZCnk16aZCSe6Gu9VZAMlpWkdhWbVT2DuZA7Bvz30zZApyH9jjG14ZC5llNvr4bgHcN",
        #     "commentId": "18126310636270791",
        #     "text": "12345"
        # }
        # ret = Laravel_Helper.LaravelApiCaller(data=data).post()
        # print (ret)



        # response = requests.post(
        #     url="https://accounts.google.com/o/oauth2/token",
        #     data={
        #         "client_id": "536277208137-okgj3vg6tskek5eg6r62jis5didrhfc3.apps.googleusercontent.com",  #TODO keep it to settings
        #         "client_secret": "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",                                 #TODO keep it to settings
        #         "grant_type": "refresh_token",
        #         "refresh_token": "1//0eEcTGHyIHZidCgYIARAAGA4SNwF-L9IrBxG90zwkR-Y7k4QoYBjY5H8JjykXbHi1QvqbVdaZPNejuNpkcxc8wjVIixgC_UKgCeQ"
        #     },)

        # print(response.status_code)
        # print(response.json())

        # code, response = api_fb_get_post_comments("EAANwBngXqOABAFgJWR0w65ZAHtLoHRVgowMqMdWUT6fMzlXylBvRbGUE3XY78X4a0YhQKrcv8WYJbpvbwKIjjESDUPZBgaZCwvbkaDSv3KJ5k1QS2bI9VwfjiQRakNkBHaKAjqZBTRND8p1m1RcKukD92CA68jPHbDBF0ocmbmIrqEENOucb", 1337332883404624, 1)
        # print(code)
        # print(response)
    
    





    # def campaign_test(self):
    #     cs = CampaignManager.get_active_campaigns()
    #     print(cs)
    #     cs = CampaignManager.get_ordering_campaigns()
    #     print(cs)

    # def cart_product_manager_test(self):
    #     campaign = Campaign.objects.get(id=1)
    #     campaign_product = CampaignProduct.objects.get(id=1)

    #     cart_product_request = CartManager.create_cart_product_request(
    #         campaign, 'facebook', '3141324909312956', 'Liu Ian', {
    #             campaign_product: 5,
    #         }
    #     )
    #     cart_product_request = CartManager.process(cart_product_request)

    # def lucky_draw_test(self):
    #     c = Campaign.objects.get(id=1)
    #     cp = CampaignProduct.objects.get(id=1)
    #     prize_cp = CampaignProduct.objects.get(id=2)

    #     # lucky_draw = CampaignLuckyDrawManager.process(
    #     #     c, DrawFromCampaignLikesEvent(c), prize_cp, 1,
    #     # )

    #     # keyword='testtest'
    #     # lucky_draw = CampaignLuckyDrawManager.process(
    #     #     c, DrawFromCampaignCommentsEvent(c, keyword), prize_cp, 1,
    #     # )

    #     lucky_draw = CampaignLuckyDrawManager.process(
    #         c, DrawFromCartProductsEvent(c, cp), prize_cp, 1,
    #     )

    #     print(lucky_draw.__dict__)

    # def cart_product_test(self):
    #     c = Campaign.objects.get(id=1)
    #     cp = CampaignProduct.objects.get(id=1)
    #     cps = cart_product.filter_cart_products(
    #         c, cp, ('order_code', 'cart'), ('valid',))
    #     print(c, cp, cps)

    # def campagin_product_test(self):
    #     cp = CampaignProduct.objects.get(id=1)
    #     r = CampaignProductStatusProcessor.update_status(
    #         cp, CampaignProductStatusProcessor.Event.DEACTIVATE)

    # def i18n_test(self):
    #     from backend.i18n.campaign_announcement import \
    #         i18n_get_campaign_announcement_lucky_draw_winner
    #     customer_name = 'John'
    #     product_name = 'Phone'
    #     print(i18n_get_campaign_announcement_lucky_draw_winner(
    #         customer_name, product_name))
    #     print(i18n_get_campaign_announcement_lucky_draw_winner(
    #         customer_name, product_name, lang='en'))
    #     print(i18n_get_campaign_announcement_lucky_draw_winner(
    #         customer_name, product_name, lang='zh-hant'))
    #     print(i18n_get_campaign_announcement_lucky_draw_winner(
    #         customer_name, product_name, lang='zh-hans'))


    # def ipg_test(self):
    #     from api.views.payment._payment import IPG_Helper
    #     chargetotal=10
    #     currency='702'
    #     timezone = "Asia/Singapore"
    #     IPG_Helper.create_payment(timezone, chargetotal, currency)

    # def youtube_test(self):
    #     ret, code = api_youtube_get_video_info_with_api_key("5qap5aO4i9A")

    #     print(f"code :{code}")
    #     print(f"ret :{ret}")

    # def campaign_test(self):
    #     campaign_job(53)

    # def subscription_code_test(self):
    #     print(SubscriptionCodeManager.generate(1,30))
    #     code = "gAAAAABiIZm30ERH6Z0sgphHgO2UrqWWltQfhTndkYFWe5YXUnSLyp2Rbushoc2QOUHphB8l4SzURX4GUJgeQ3CP5xw5BNadkIYncsE6-p19KWaL12XzTJvIC42LeaMaQDPFvFdju2SU32S-XiOjSDLwKGPH4LiOHWHCh02uhO1sQb8kcKPZ-oRMYk3iKxsqHDURvh9M4cIHNQi3OTr_DX60w_ZALRHEZQ=="
    #     SubscriptionCodeManager.execute(code,'facebook',1)

# $stringToHash = $this->storeId . $this->txndatetime . $this->chargetotal . $this->currency . $this->sharedSecret;
#         $ascii = bin2hex($stringToHash);

#         return hash("sha256", $ascii);
    def add_user_subscription_user(self):
        UserSubscription.objects.get(id=1).root_users.add(User.objects.get(id=44))

    def test_text_classifier(self):
        from backend.api.nlp.classify import classify_comment_v1

        print(classify_comment_v1(texts=[['Deliver Delivery delivery','payment payment payment']],threshold=0.7))

    def test_pre_order_helper(self):
        from api.utils.common.order_helper import PreOrderHelper
        from api.models.user.user import User
        from api.models.order.pre_order import PreOrder
        from api.models.campaign.campaign_product import CampaignProduct
        from api.models.order.order_product import OrderProduct

        api_user = User.objects.get(id=1)
        pre_order = PreOrder.objects.get(id=506)
        # campaign_product = CampaignProduct.objects.get(id=7400)
        

        # order_product = OrderProduct.objects.get(id=252464)
        # PreOrderHelper.add_product(api_user,pre_order,campaign_product,1)
        # PreOrderHelper.update_product(api_user,pre_order,order_product,2)
        # PreOrderHelper.delete_product(api_user,pre_order,order_product)
        PreOrderHelper.checkout(api_user,pre_order)

    def test_ipg_success_hash(self):
        import hmac
        import hashlib 
        import binascii
        # approval_code|chargetotal|currency|txndatetime|storename
        # chargetotal|currency|txndatetime|storename|approval_code

        #sharedsecret + approval_code + chargetotal + currency + txndatetime + storename

        approval_code = 'Y:048993:3556730117:PPX :208910903298'
        chargetotal= '0.10'
        currency = '702'
        txndatetime = '2022:03:30-18:10:33'
        store_name = "4530042983"
        secret = 'Xe33QM7UTs'

        ascii = binascii.b2a_hex((secret+approval_code+chargetotal+currency+txndatetime+store_name).encode())   
        hash = hashlib.sha256(ascii).hexdigest()
        print(hash)
        # hash = hmac.new(secret.encode(), (secret+approval_code+chargetotal+currency+txndatetime+store_name).encode(), hashlib.sha256).hexdigest()
        # print(hash)

    def test_mongodb_query(self):
        from backend.pymongo.mongodb import db

        print(db.api_campaign_comment.find({"campaign_id":365}).count())