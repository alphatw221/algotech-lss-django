import email
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
from backend.api.instagram.post import api_ig_private_message, api_ig_get_post_comments
from backend.api.twitch.post import api_twitch_get_access_token
from backend.i18n.register_confirm_mail import i18n_get_register_confirm_mail_content, i18n_get_register_confirm_mail_subject, i18n_get_register_activate_mail_subject


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # self.test_mongodb_query()
        self.test_user_plan()
        # ret = api_twitch_get_access_token()
        # print (ret)


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

    
    def test_mongodb_query(self):
        from backend.pymongo.mongodb import db
        from api.utils.advance_query.dashboard import get_total_revenue, get_order_total_sales, get_pre_order_total_sales, \
        get_order_total_sales_by_month,get_campaign_comment_rank, get_campaign_order_rank, get_campaign_complete_sales, get_total_order_complete_proceed,\
        get_total_pre_order_count, get_campaign_order_complete_proceed,get_total_average_sales,get_total_average_comment_count,get_campaign_merge_order_list

        print(get_campaign_merge_order_list(381))

    def test_set_password(self):

        from django.contrib.auth.models import User as AuthUser

        auth_user = AuthUser.objects.get(id=87)

        auth_user.set_password(" ally@algotech.app")
        auth_user.save()

    def test_send_email(self):

        from backend.python_rq.python_rq import email_queue
        from automation.jobs.send_email_job import send_email_job
        # kwargs={
        #         "email": 'derekhwang33@gmail.com', 
        #         "template_name": "register_confirmation.html",
        #         "content": None,
        #         "parameters": {
        #             'firstName': 'Derek',
        #             'email': 'test@gmail.com',
        #             'password': 'aaaaaaaaaaa'
        #         },
        #         "file": None, 
        #     }
        # send_email_job(**kwargs)
        
        # email_queue.enqueue(send_email_job,args=('alphatw22193@gmail.com', None, "test", None, None, None), result_ttl=10, failure_ttl=10)
        email_queue.enqueue(
            send_email_job,
            kwargs={
                "subject": i18n_get_register_activate_mail_subject(),
                "email": 'derekhwang33@gmail.com', 
                "template_name": "register_confirmation.html",
                "parameters": {
                    'firstName': 'Derek',
                    'email': 'test@gmail.com',
                    'password': 'aaaaaaaaaaa'
                },
                "file": None, 
            }, result_ttl=10, failure_ttl=10)
    
    def test_user_plan(self):
        import business_policy
        
        # print([cls.__name__ for cls in LSSPlan.__bases__])