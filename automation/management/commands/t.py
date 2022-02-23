import imp
import pprint
import requests

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.cart.cart_product import CartProduct
from api.utils.orm import campaign_comment, cart_product
from backend.api.facebook.page import *
from backend.api.facebook.post import *
from backend.api.facebook.user import *
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
from backend.cart.cart_product.request import CartProductRequest
from backend.comment_catching.facebook.post_comment import *
from django.core.management.base import BaseCommand
from api.views.order.order_report import *
from backend.pymongo.mongodb import db
from api.models.youtube.youtube_channel import YoutubeChannel
from automation.jobs.campaign_job import *
from backend.api.instagram.user import *
from backend.api.youtube.viedo import api_youtube_get_video_info_with_api_key
from automation.jobs.campaign_job import campaign_job
from mail.sender.sender import *
from api.views.payment.payment import * 


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
        
        # self.campaign_test()
        # self.ipg_test()
        # self.youtube_test()
        # campaign_job(109)
        # send_email(273)
        # code,data = api_google_post_refresh_token("1//0eEcTGHyIHZidCgYIARAAGA4SNwF-L9IrBxG90zwkR-Y7k4QoYBjY5H8JjykXbHi1QvqbVdaZPNejuNpkcxc8wjVIixgC_UKgCeQ")
        # print(code)
        # print(data)

        from dataclasses import dataclass
        from backend.api._api_caller import RestApiJsonCaller
        class Laravel_Helper:
            @dataclass
            class LaravelApiCaller(RestApiJsonCaller):
                domain_url: str = "https://v1login.liveshowseller.com/api/ig_private_msg"
        
        data = {
            "accessToken": "EAANwBngXqOABAOy6CE0qFi92dImqOwDIWzvNzyvD0PNsLt0WqUIJiwNzZBbLvkEb1s1SlRUZAIPiI4Pw143KFiTfkbozmDnzZCrTY5Dj4J30qHVvVJejIyeZCnk16aZCSe6Gu9VZAMlpWkdhWbVT2DuZA7Bvz30zZApyH9jjG14ZC5llNvr4bgHcN",
            "commentId": "18126310636270791",
            "text": "12345"
        }
        ret = Laravel_Helper.LaravelApiCaller(data=data).post()
        print (ret)



        # response = requests.post(
        #     url="https://accounts.google.com/o/oauth2/token",
        #     data={
        #         "client_id": "536277208137-okgj3vg6tskek5eg6r62jis5didrhfc3.apps.googleusercontent.com",  #TODO keep it to settings
        #         "client_secret": "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",                                 #TODO keep it to settings
        #         "grant_type": "refresh_token",
        #         "refresh_token": "1//0eEcTGHyIHZidCgYIARAAGA4SNwF-L9IrBxG90zwkR-Y7k4QoYBjY5H8JjykXbHi1QvqbVdaZPNejuNpkcxc8wjVIixgC_UKgCeQ"
        #     },)

        # {'data': [
        # {'created_time': 1645082006, 'from': {'picture': {'data': {'height': 50, 'is_silhouette': False, 'url': 'https://platform-lookaside.fbsbx.com/platform/profilepic/?psid=5067502543282908&height=50&width=50&ext=1647675113&hash=AeQpm_5_PDZj1M78x9U', 'width': 50}}, 'name': 'Nivea Chen', 'id': '5067502543282908'}, 'message': 'hihi', 'id': '1337332883404624_1337334940071085'},
        # {'created_time': 1645082015, 'message': 'Test', 'id': '1337332883404624_1337335016737744'}, 
        # {'created_time': 1645082211, 'from': {'picture': {'data': {'height': 50, 'is_silhouette': False, 'url': 'https://platform-lookaside.fbsbx.com/platform/profilepic/?psid=5067502543282908&height=50&width=50&ext=1647675113&hash=AeQpm_5_PDZj1M78u6w', 'width': 50}}, 'name': 'Nivea Chen', 'id': '5067502543282908'}, 'message': 'roll+2', 'id': '1337332883404624_1337336250070954'},
        #  {'created_time': 1645082213, 'message': 'roll + 1', 'id': '1337332883404624_1337336270070952'}, 
        #  {'created_time': 1645082214, 'message': 'Roll', 'id': '1337332883404624_1337336276737618'}, 
        #  {'created_time': 1645082219, 'from': {'picture': {'data': {'height': 50, 'is_silhouette': False, 'url': 'https://platform-lookaside.fbsbx.com/platform/profilepic/?psid=4056786737668879&height=50&width=50&ext=1647675113&hash=AeSyFzud7adj0gNB5k8', 'width': 50}}, 'name': 'Vanessa Mao', 'id': '4056786737668879'}, 'message': 'roll+1', 'id': '1337332883404624_1337336316737614'},
        #   {'created_time': 1645082220, 'message': 'roll + 1', 'id': '1337332883404624_1337336326737613'}, 
        #   {'created_time': 1645082249, 'message': 'Roll + 1', 'id': '1337332883404624_1337336540070925'}, 
        #   {'created_time': 1645082350, 'message': 'roll+1', 'id': '1337332883404624_1337337123404200'}, 
        #   {'created_time': 1645082629, 'from': {'picture': {'data': {'height': 50, 'is_silhouette': False, 'url': 'https://platform-lookaside.fbsbx.com/platform/profilepic/?psid=4422762234485468&height=50&width=50&ext=1647675113&hash=AeQcZihQT9jAIWQSVT4', 'width': 50}}, 'name': 'Yi-Hsueh Lin', 'id': '4422762234485468'}, 'message': 'test', 'id': '1337332883404624_1337338806737365'}, 
        #   {'created_time': 1645083036, 'from': {'picture': {'data': {'height': 50, 'is_silhouette': False, 'url': 'https://platform-lookaside.fbsbx.com/platform/profilepic/?psid=4869164659762789&height=50&width=50&ext=1647675113&hash=AeTQZNW5Bg_V6HpthCk', 'width': 50}}, 'name': 'Derek Hwang', 'id': '4869164659762789'}, 'message': 'roll +1', 'id': '1337332883404624_1337341230070456'}], 'paging': {'cursors': {'before': 'QVFIUmUxRWl5YlljMWlfWVNPWVN2dk9lV2duZAS1Rak5Ha0I2TVFsSTRkV2pXNlVnYkFSSS1yOG1BUnJxTjhSUHM2c0dlY0xpaDlScHdFRmlqLVFETGdJMjlR', 'after': 'QVFIUlVpakExd0VmcGpPSXQtQnZA2WHJUZA0RsakxwNl9UNGhNRl9ERjlnOUhxS3RZAQUx3N1hHeXpJN0U3YVNTZA2ZA5SnNYWVdQZA3djSkRrcXgwYmFmdm5wVTdB'}}}


        # print(response.status_code)
        # print(response.json())

        # code, response = api_fb_get_post_comments("EAANwBngXqOABAFgJWR0w65ZAHtLoHRVgowMqMdWUT6fMzlXylBvRbGUE3XY78X4a0YhQKrcv8WYJbpvbwKIjjESDUPZBgaZCwvbkaDSv3KJ5k1QS2bI9VwfjiQRakNkBHaKAjqZBTRND8p1m1RcKukD92CA68jPHbDBF0ocmbmIrqEENOucb", 1337332883404624, 1)
        # print(code)
        # print(response)

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
        ret, code = api_youtube_get_video_info_with_api_key("5qap5aO4i9A")

        print(f"code :{code}")
        print(f"ret :{ret}")

    def campaign_test(self):
        campaign_job(53)
# $stringToHash = $this->storeId . $this->txndatetime . $this->chargetotal . $this->currency . $this->sharedSecret;
#         $ascii = bin2hex($stringToHash);

#         return hash("sha256", $ascii);