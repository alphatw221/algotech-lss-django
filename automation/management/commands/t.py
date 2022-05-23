import email
import imp
from inspect import Parameter
import pprint
from grpc import server
import requests


from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.cart.cart_product import CartProduct
from api.models.user.user import User
from api.models.user.user_subscription import UserSubscription
from api.utils.orm import campaign_comment, cart_product
import backend
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
from datetime import datetime
from backend.api.instagram.post import api_ig_private_message, api_ig_get_post_comments
from backend.api.twitch.post import api_twitch_get_access_token
from backend.i18n.register_confirm_mail import i18n_get_register_confirm_mail_content, i18n_get_register_confirm_mail_subject, i18n_get_register_activate_mail_subject
import service
from api import models
class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # self.test_user_plan()
        self.test_websocket()

    def modify_database(self):
        from api.models.user.user_subscription import UserSubscription
        from api.models.user.user import User
        from django.contrib.auth.models import User as AuthUser
        from json import loads, dumps
        from collections import OrderedDict
        import json
        import re
        from api.models.campaign.campaign import Campaign
        def to_dict(input_ordered_dict):
            return loads(dumps(input_ordered_dict))
        def add_activated_country():
            for obj in UserSubscription.objects.filter(id=1):
                obj.meta_country['activated_country'] = ["PH"]
                obj.save()
        def modify_meta_payment_from_user_subscription():
            for obj in UserSubscription.objects.all():
                direct_payment = to_dict(obj.meta_payment.get("direct_payment", {}))
                first_data = to_dict(obj.meta_payment.get("firstdata", {}))
                pay_mongo = to_dict(obj.meta_payment.get("paymongo", {}))
                print("-------------------------------")
                if direct_payment:
                    string_dp = json.dumps(direct_payment)
                    regex = re.compile(r"distinct_payment")
                    string_dp = regex.sub("direct_payment", string_dp)
                    new_dict = json.loads(string_dp)
                    
                    obj.meta_payment["direct_payment"] = new_dict
                    print(new_dict)
                    
                if first_data:
                    string_dp = json.dumps(first_data)
                    regex = re.compile(r"firstdata")
                    string_dp = regex.sub("first_data", string_dp)
                    regex = re.compile(r"ipg")
                    string_dp = regex.sub("first_data", string_dp)
                    new_dict = json.loads(string_dp) 
                    
                    obj.meta_payment["first_data"] = new_dict
                    del obj.meta_payment["firstdata"]
                    print(new_dict)
                if pay_mongo:
                    string_dp = json.dumps(pay_mongo)
                    regex = re.compile(r"paymongo")
                    string_dp = regex.sub("pay_mongo", string_dp)
                    new_dict = json.loads(string_dp)
                    obj.meta_payment["pay_mongo"] = new_dict
                    del obj.meta_payment["paymongo"]
                    print(new_dict)
                obj.save()
        def modify_meta_payment_from_campaign():
            for obj in Campaign.objects.all().order_by("-id"):
                print("id", obj.id)
                if obj.id:
                    new_mata_payment = to_dict(obj.meta_payment.get("sg", {}))
                #     print(new_mata_payment)
                    direct_payment = to_dict(new_mata_payment.get("direct_payment", {}))
                    first_data = to_dict(new_mata_payment.get("firstdata", {}))
                    pay_mongo = to_dict(new_mata_payment.get("paymongo", {}))
                #     print(direct_payment)
                #     print(first_data)
                #     print(pay_mongo)
                    print("-------------------------------")
                    if direct_payment:
                        string_dp = json.dumps(direct_payment)
                        regex = re.compile(r"distinct_payment")
                        string_dp = regex.sub("direct_payment", string_dp)
                        new_dict = json.loads(string_dp)

                        new_mata_payment["direct_payment"] = new_dict
                #         print(new_dict)

                    if first_data:
                        string_dp = json.dumps(first_data)
                        regex = re.compile(r"firstdata")
                        string_dp = regex.sub("first_data", string_dp)
                        regex = re.compile(r"ipg")
                        string_dp = regex.sub("first_data", string_dp)
                        new_dict = json.loads(string_dp) 

                        new_mata_payment["first_data"] = new_dict
                        del new_mata_payment["firstdata"]
                #         print(new_dict)
                    if pay_mongo:
                        string_dp = json.dumps(pay_mongo)
                        regex = re.compile(r"paymongo")
                        string_dp = regex.sub("pay_mongo", string_dp)
                        new_dict = json.loads(string_dp)
                        new_mata_payment["pay_mongo"] = new_dict
                        del new_mata_payment["paymongo"]
                #         print(new_dict)
                    if new_mata_payment:
                        print(new_mata_payment)
                        obj.meta_payment = new_mata_payment
                        obj.save()
        
        add_activated_country()
        modify_meta_payment_from_user_subscription()
        modify_meta_payment_from_campaign()
        
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

        print(get_total_revenue(1))

    def test_set_password(self):

        from django.contrib.auth.models import User as AuthUser

        auth_user = AuthUser.objects.get(id=7)

        auth_user.set_password("123456")
        auth_user.save()

    def test_send_email(self):
        
        service.email.email_service.EmailService.send_email_template('test','alphatw22193@gmail.com',
            "email_reset_password_link.html",
            {"url":settings.GCP_API_LOADBALANCER_URL +"/lss/#/password/reset","code":"1234","username":"test"},
            lang='en')
    
    def test_user_plan(self):

        api_user_subscription = models.user.user_subscription.UserSubscription.objects.get(id=1)
        
        if datetime.timestamp(datetime.now())>datetime.timestamp(api_user_subscription.expired_at):
            print('true')
            return
        print('false')
        expired_date = api_user_subscription.expired_at.date()
        started_date = api_user_subscription.started_at.date()
        
        today = datetime.now().date()
        # print((expired_date-today).days)
        # print((expired_date-started_date).days)
        adjust_amount = api_user_subscription.purchase_price*((expired_date-today).days/(expired_date-started_date).days)
        print(adjust_amount)

    def test_sendinblue(self):
        
        import service

        sib_service = service.sendinblue

        # sib.transaction_email.ResetPasswordLinkEmail(url="url",code="code",username="username",to="alphatw22193@gmail.com").send()
        
        # sib_service.transaction_email.AccountActivationEmail(first_name="first_name",plan="plan",email="email",password="password", to="alphatw22193@gmail.com", country="SG").send()

        order = db.api_order.find_one({'id': 32410})
        del order['_id']
        campaign_id = order['campaign_id']
        campaign = db.api_campaign.find_one({'id': int(campaign_id)})
        del campaign['_id']
        facebook_page_id = campaign['facebook_page_id']
        shop = db.api_facebook_page.find_one({'id': int(facebook_page_id)})['name']
        
        sib_service.transaction_email.OrderConfirmationEmail(shop=shop, order=order, campaign=campaign, to=["derekhwang33@gmail.com"], cc=[]).send()
        print ('poooooop')

        # sib.transaction_email.RegistraionConfirmationEmail(first_name="first_name",email="email",password="password", to="alphatw22193@gmail.com").send()

    def test_hubspot(self):
        import service
        from datetime import datetime
        # import pytz
        service.hubspot.contact.update("651",properties={"expiry_date":int(datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0).timestamp()*1000)})
        # service.hubspot.contact.update("651",properties={"expiry_date":1652054400})
    def test_nlp(self):

        import service

        print(service.nlp.classification.classify_comment_v1([['test test']]))
    
    def test_mongo_aggr(self):
        from pprint import pprint 
        # cursor = db.api_user_subscription.aggregate([
        #     {'$match': {'id': 1}},
        #     {'$lookup': {
        #         'from': 'api_campaign',
        #         'as': 'campaigns',
        #         'let': { 'id': '$id' },
        #         'pipeline': [
        #             {'$match': {
        #                 '$expr': { '$eq': [ '$$id', '$user_subscription_id' ] },
        #                 'id': {'$ne': None}
        #             }},
        #             {'$project': { '_id': 0, 'id': 1 }}
        #         ]
        #     }}
        # ])
        # l = list(cursor)
        # pprint (l)

        # cursor = db.api_campaign.aggregate([
        #     {'$match': {'id': 118}},
        #     {'$lookup': {
        #         'from': 'api_order',
        #         'as': 'orders',
        #         'let': { 'id': '$id' },
        #         'pipeline': [
        #             {'$match': {
        #                 '$expr': { '$eq': [ '$$id', '$campaign_id'] }
        #             }},
        #             # {'$unwind': '$orders'},
        #             {'$group': {
        #                 '_id': '$customer_id',
        #                 'customer_id': { '$first': '$customer_id'},
        #                 'customer_name': { '$first': '$customer_name'},
        #                 'customer_img': { '$first': '$customer_img'},
        #                 'shipping_email': { '$first': '$shipping_email'},
        #                 'shipping_phone': { '$first': '$shipping_phone'},
        #                 'platform': { '$first': '$platform'},
        #             }}
        #         ],
        #     }},
        #     {'$unwind': '$orders'},
        #     {'$project': {'_id': 0, 'orders': 1, }},
        #     # {'$unwind': '$orders'}
        # ])
        # l = list(cursor)
        # pprint (l)


        cursor = db.api_user_subscription.aggregate([
            {'$match': {'id': 1}},
            {'$lookup': {
                'from': 'api_campaign',
                'as': 'campaigns',
                'let': { 'id': '$id' },
                'pipeline': [
                    {'$match': {
                        '$expr': { '$eq': [ '$$id', '$user_subscription_id' ] },
                        'id': {'$ne': None}
                    }},
                    {'$project': { '_id': 0, 'id': 1 }},
                    {'$lookup': {
                        'from': 'api_order',
                        'as': 'orders',
                        'let': { 'id': '$id' },
                        'pipeline': [
                            {'$match': {
                                '$expr': { '$eq': [ '$$id', '$campaign_id'] }
                            }}
                        ],
                    }},
                    {'$unwind': '$orders'},  
                    {'$match': {'orders': {'$ne': []}}},
                    {'$project': {'_id': 0, 'orders': 1}},
                ]
            }},
            {'$unwind': '$campaigns'},  
            {'$project': { '_id': 0, 'campaigns': 1 }},
            {'$group': {
                '_id': '$campaigns.orders.customer_id',
                'customer_id': { '$first': '$campaigns.orders.customer_id'},
                'customer_name': { '$first': '$campaigns.orders.customer_name'},
                'customer_img': { '$first': '$campaigns.orders.customer_img'},
                'shipping_email': { '$first': '$campaigns.orders.shipping_email'},
                'shipping_phone': { '$first': '$campaigns.orders.shipping_phone'},
                'platform': { '$first': '$campaigns.orders.platform'},
            }},
        ])
        l = list(cursor)
        pprint(l)

    def test_websocket(self):

        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.send)("channel_name", {"type": "chat.force_disconnect"})
        # async_to_sync(channel_layer.group_send)("user_subscription_1", {"type": "notification_message","data":{"message":"testmessage"}})

        async_to_sync(channel_layer.group_send)("campaign_440", {"type": "comment_data","data":{"message":"testmessage"}})
        async_to_sync(channel_layer.group_send)("campaign_440", {"type": "order_data","data":{"message":"testmessage"}})
        async_to_sync(channel_layer.group_send)("campaign_440", {"type": "product_data","data":{"message":"testmessage"}})