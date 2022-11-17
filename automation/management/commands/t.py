import random
import string
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.core.management.base import BaseCommand
from automation.jobs.send_reminder_messages import send_reminder_messages_job
import database
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import arrow
import business_policy
import lib
import service
from api import models, rule
from api.models.user.promotion_code import PromotionCode
from api.models.user.user import AuthUserSerializer
from api.utils.common.verify import ApiVerifyError, Verify
from api.utils.error_handle.error_handler.api_error_handler import \
    api_error_handler
from api.utils.orm.deal import record_subscription_for_trial_user
from business_policy.marketing_plan import MarketingPlan


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.test_cart_expired_adjustment()
        pass


    def modify_database(self):

        import json
        import re
        from collections import OrderedDict
        from json import dumps, loads

        from django.contrib.auth.models import User as AuthUser

        from api.models.campaign.campaign import Campaign
        from api.models.user.user import User
        from api.models.user.user_subscription import UserSubscription
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
        models.user.user_subscription.UserSubscription.objects.get(id=1).root_users.add(models.user.user.User.objects.get(id=44))

    def test_text_classifier(self):
        from backend.api.nlp.classify import classify_comment_v1

        print(classify_comment_v1(texts=[['Deliver Delivery delivery','payment payment payment']],threshold=0.7))

    def test_pre_order_helper(self):
        from api.models.campaign.campaign_product import CampaignProduct
        from api.models.order.order_product import OrderProduct
        from api.models.order.pre_order import PreOrder
        from api.models.user.user import User
        from api.utils.common.order_helper import PreOrderHelper

        api_user = User.objects.get(id=1)
        pre_order = PreOrder.objects.get(id=506)
        # campaign_product = CampaignProduct.objects.get(id=7400)
        # order_product = OrderProduct.objects.get(id=252464)
        # PreOrderHelper.add_product(api_user,pre_order,campaign_product,1)
        # PreOrderHelper.update_product(api_user,pre_order,order_product,2)
        # PreOrderHelper.delete_product(api_user,pre_order,order_product)
        PreOrderHelper.checkout(api_user,pre_order)

    
    def test_mongodb_query(self):
        from pprint import pprint

        import database

        # from backend.pymongo.mongodb import db
        # from api.utils.advance_query.dashboard import get_total_revenue, get_order_total_sales, get_pre_order_total_sales, \
        # get_order_total_sales_by_month,get_campaign_comment_rank, get_campaign_order_rank, get_campaign_complete_sales, get_total_order_complete_proceed,\
        # get_total_pre_order_count, get_campaign_order_complete_proceed,get_total_average_sales,get_total_average_comment_count,get_campaign_merge_order_list
        # print(get_total_revenue(1))
        # campaign_products = database.lss.campaign.get_ongoing_campaign_disallow_overbook_campaign_product()
        pre_orders = database.lss.pre_order.get_pre_order_contain_campaign_product(9381)
        pprint(pre_orders)

    def test_set_password(self):

        from django.contrib.auth.models import User as AuthUser

        auth_user = AuthUser.objects.get(id=685)
        auth_user.set_password("hmh1730")
        auth_user.save()

    def test_send_email(self):
        
        import lib
        from api import models
        from automation import jobs
        order = models.order.order.Order.objects.get(id=32560)
        content = lib.helper.order_helper.OrderHelper.get_confirmation_email_content(order)
        jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)


        # service.email.email_service.EmailService.send_email_template('test','alphatw22193@gmail.com',
        #     "email_reset_password_link.html",
        #     {"url":settings.GCP_API_LOADBALANCER_URL +"/lss/#/password/reset","code":"1234","username":"test"},
        #     lang='en')
    
    def test_user_plan(self):
        from datetime import datetime

        from api import models
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
        from database.lss._config import db
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
        from datetime import datetime

        import service

        # import pytz
        service.hubspot.contact.update("651",properties={"expiry_date":int(datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0).timestamp()*1000)})
        # service.hubspot.contact.update("651",properties={"expiry_date":1652054400})
    def test_nlp(self):

        import service
        categories = service.nlp.classification.classify_comment_v2([
        '包裹在哪',
        'I would like to have a refund',
        '满多少可以包邮',
        '我想要紅色的還有嗎',
        'what time could be free',
        '不滿意可以退費嗎',
        '你們可以用什麼信用卡',
        '台南滷肉飯',
        '商品一件多少錢',
        '請問這個還有貨嗎'
        ])
        print(categories)

    
    def test_mongo_aggr(self):
        from pprint import pprint

        import database
        l = database.lss.campaign.get_merge_order_list_pagination(campaign_id=958, status='', search='', filter_payment=[], filter_delivery=[], filter_platform=[])
        pprint(l)

    def test_websocket(self):
        import database
        import service

        # from asgiref.sync import async_to_sync
        # from channels.layers import get_channel_layer

        # channel_layer = get_channel_layer()
        # # async_to_sync(channel_layer.send)("channel_name", {"type": "chat.force_disconnect"})
        # # async_to_sync(channel_layer.group_send)("user_subscription_1", {"type": "notification_message","data":{"message":"testmessage"}})
        # async_to_sync(channel_layer.group_send)("campaign_1356", {"type": "cart_data","data":{"message":"123"}})
        # async_to_sync(channel_layer.group_send)("campaign_440", {"type": "order_data","data":{"message":"testmessage"}})
        # async_to_sync(channel_layer.group_send)("campaign_440", {"type": "product_data","data":{"message":"testmessage"}})
        pymongo_cart = database.lss.cart.Cart.get_object(id=2)
        service.channels.campaign.send_cart_data(1356, pymongo_cart.data)

    def test_lucky_draw(self):

        import lib
        from api import models

        campaign = models.campaign.campaign.Campaign.objects.get(id=510)
        candidate_set = lib.helper.lucky_draw_helper.KeywordCandidateSetGenerator.get_candidate_set(campaign,'cart',repeatable=True)
        campaign_product = models.campaign.campaign_product.CampaignProduct.objects.get(id=7819)

        print(candidate_set)

        winner_list = lib.helper.lucky_draw_helper.LuckyDraw.draw_from_candidate(campaign, campaign_product,  candidate_set=candidate_set)

        print(winner_list)

    def test_order_helper(self):

        import lib
        from api import models


        lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_id=821, campaign_product_id=7648,qty=2)
        # pre_order = lib.helper.order_helper.PreOrderHelper.update_product(None, 821, 253873, 2)

        # lib.helper.order_helper.PreOrderHelper.delete_product(None, 821, 253873)
        # success, order = lib.helper.order_helper.PreOrderHelper.checkout(None, campaign_id=449, pre_order_id=821)
        
        # if success:
        #     print('success')
        # else:
        #     print('unsuccess')

        # print(order.data)
        # lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order_id=975, campaign_product_id=7817,qty=1)
        # lib.helper.order_helper.PreOrderHelper.update_product(None, 975, 253601, 2)
        # lib.helper.order_helper.PreOrderHelper.delete_product(None, 975, 253601)
        # lib.helper.order_helper.PreOrderHelper.checkout(None, campaign_id=510, pre_order_id=975)
    
    def test_campaign_job(self):


        from automation import jobs
        jobs.campaign_job.campaign_job(661)

        from datetime import datetime

        from dateutil import parser

        from database.lss._config import db
        ig_datas = db.api_campaign_comment.find({'platform': 'instagram'})
        for ig_data in ig_datas:
            _id = ig_data['_id']
            created_time = ig_data['created_time']
            if type(created_time) == str:
                timestamp = datetime.timestamp(parser.parse(created_time))
                
                print (_id)
                db.api_campaign_comment.update_one(
                    {'_id': _id},
                    {'$set': {'created_time': timestamp}}
                )


        ig_datas = db.api_campaign_comment.find({'platform': 'instagram'})
        for ig_data in ig_datas:
            _id = ig_data['_id']
            created_time = ig_data['created_time']
            if type(created_time) == str:
                timestamp = datetime.timestamp(parser.parse(created_time))
                
                print (_id)
                db.api_campaign_comment.update_one(
                    {'_id': _id},
                    {'$set': {'created_time': timestamp}}
                )

    def test_hitpay_verification(self):


        import hashlib
        import hmac

        KEY_LIST = ['amount', 'currency', 'payment_id', 'payment_request_id', 'phone', 'reference_number', 'status']

        salt = '9ntt8RQoPtP9NXlO36aZTpP5wK10vFWbsw45KjaBGNzfYiU75cUJ3LLCEqMLGUO9'

        request_data = {'payment_id': '96ec6ec3-fea0-4a9d-bd38-0b9bb05b1f24', 
        'payment_request_id': '96ec6ec3-2dcb-4aca-ad54-d29fde47a3c3', 
        'phone': '', 
        'amount': '1.00', 
        'currency': 'SGD', 
        'status': 'completed', 
        'reference_number': '32846',
         'hmac': 'bcf1e64ffd1214f3af65202dc2072b221c25fdc221b540559b7d563f5a454b8d'}

        # bcf1e64ffd1214f3af65202dc2072b221c25fdc221b540559b7d563f5a454b8d

        data=''
        for key in KEY_LIST:
            data = data+(key+request_data.get(key,''))
        print('data:')
        print(data)

        hexdig = hmac.new(salt.encode(), msg=data.encode(), digestmod=hashlib.sha256).hexdigest()

        print('hexdig:')
        print(hexdig)


    def test_cart_helper(self):

        import lib
        from api import models

        campaign = models.campaign.campaign.Campaign.objects.get(id=1024)
        models.cart.cart.Cart.objects.create(
            customer_id='testing',
            customer_name = 'test',
            customer_img = '',
            platform = 'facebook',
            campaign=campaign
        )

    def test_easy_store(self):
        from automation import jobs

        jobs.easy_store.export_product_job(618,{
        "shop": "keepsake.easy.co",
        "access_token": "bb11090512508f226d8e6c457402ae27"
      })

        # from plugins.easy_store import service
        # from pprint import pprint

        # shop = 'yihsuehlinlinyixue.easy.co'
        # access_token = '698f9a9a7c8bbe5f65d0207fb6cba139'
        # #product
        # # success, data = service.products.get_published_product(shop=shop, access_token=access_token,page=1)
        
        # #checkout
        # # line_items =  [
        # #             {
        # #                 "variant_id": 36344238,
        # #                 "quantity": 2
        # #             }
        # #         ]
            
        # # success, data = service.checkouts.create_checkout(shop, access_token, line_items)
        

        # # success, data = service.checkouts.retrieve_checkout(shop, access_token, '64ef5862-4685-4aad-ae33-2d2d82428115')
        # # success, data =  service.checkouts.update_checkout(shop, access_token, line_items, '64ef5862-4685-4aad-ae33-2d2d82428115')
        # # pprint(success)
        # # pprint(data)

        # # a5318e0f-2317-445c-9c71-ab6c812666e9

        # # success, data =  service.checkouts.retrieve_checkout(shop=shop, access_token=access_token, cart_token='a5318e0f-2317-445c-9c71-ab6c812666e9')
        # # success, data =  service.checkouts.update_checkout(shop=shop, access_token=access_token, line_items=line_items, cart_token='a5318e0f-2317-445c-9c71-ab6c812666e9')



        # #webhook

        # # topic= 'order/create'
        # # url = 'https://staginglss.accoladeglobal.net/api/plugin/easy_store/order/webhook/create/'

        # # topic= 'order/paid'
        # # url = 'https://staginglss.accoladeglobal.net/api/plugin/easy_store/order/webhook/paid/'

        # # success, data = service.webhooks.list_webhook(shop, access_token)
        # success, data = service.webhooks.delete_webhook(shop, access_token, 1930323)
        # # success, data = service.webhooks.create_webhook(shop, token=access_token, topic=topic, url=url )

        # #order
        # # success, data = service.orders.retrieve_order(shop, access_token, 37069894)
        # # success, data = service.orders.update_order(shop, access_token, {'remark':123}, 37069894)
        # # success, data = service.orders.list_order(shop, access_token, created_at_min='2022-08-23 08:18:00')

        # # 2022-08-23T08:18:22+00:00
        # # metafields
        # pprint(success)
        # pprint(data)

    def test_remove_campaign_comment_duplicate(self):

        from database.lss._config import db

        curser = db.api_campaign_comment.aggregate([{"$group" : { "_id": {"platform":"$platform","id":"$id","campaign_id":"$campaign_id"}, "count": { "$sum": 1 } } },
            {"$match": {"_id" :{ "$ne" : None } , "count" : {"$gt": 1} } }, 
            {"$project": {"index" : "$_id", "_id" : 0} }])

        duplicate_list = list(curser)
        print(len(duplicate_list))
        # for item in duplicate_list:

        #     index = item.get('index')
        #     db.api_campaign_comment.delete_many(index)
            # print(index)
            # break
    
    def test_twitch(self):
        import service

        ret = service.twitch.twitch.whisper_to_user('17uulrj9lsj7zqpwrvsneildfcs947', '818419850', 'eat poop poop')
        print (ret)

    def test_create_developer(self):
        import base64
        import random
        import string
        import uuid

        from api import models
        data = {
            "api_key" : base64.urlsafe_b64encode(uuid.uuid4().bytes).rstrip(b'=').decode('ascii'),
            "secret_key" : ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(12)),
            "name" : 'Mr.Modi',
            "phone" : '+918401060120',
        }
        print(data)
        models.user.developer.Developer.objects.create(**data)

    def test_generate_developer_token(self):
        import base64
        import hashlib
        import hmac
        import json
        from datetime import datetime, timedelta

        from django.conf import settings

        from api import models

        header_data = {
            'alg':'sha256',
            'typ':'v1'
        }
        header_json = json.dumps(header_data)
        header = base64.urlsafe_b64encode(header_json.encode('utf-8')).rstrip(b'=').decode('utf-8')

        developer = models.user.developer.Developer.objects.get(api_key='7bbdrA5kQ06nAZP9ieEhTA')

        payload_1_data = {
            'key':developer.api_key, 
            'perm':developer.permissions,
            'auth':developer.authorization,
            'meta':developer.meta,
            'exp':int((datetime.now()+timedelta(days=7)).timestamp())
        }
        payload_1_json = json.dumps(payload_1_data)
        payload_1 = base64.urlsafe_b64encode(payload_1_json.encode('utf-8')).rstrip(b'=').decode('utf-8')

        head_and_claim = header+'.'+payload_1
        signature_1 = hmac.new(settings.SECRET_KEY.encode(), msg=head_and_claim.encode(), digestmod=hashlib.sha256).hexdigest()

        secret_key_hash_bytes = hmac.new(settings.SECRET_KEY.encode(), msg=developer.secret_key.encode(), digestmod=hashlib.sha256).digest()

        secret_key_hash = base64.urlsafe_b64encode(secret_key_hash_bytes).rstrip(b'=').decode('utf-8')
        token = head_and_claim+'.'+signature_1+'.'+developer.api_key+'.'+secret_key_hash


        print(token)

    def test_discripting_token(self):
        import base64
        import hashlib
        import hmac
        import json
        from datetime import datetime, timedelta

        from django.conf import settings

        from api import models

        token = 'eyJhbGciOiAic2hhMjU2IiwgInR5cCI6ICJ2MSJ9.eyJrZXkiOiAiN2JiZHJBNWtRMDZuQVpQOWllRWhUQSIsICJwZXJtIjoge30sICJhdXRoIjogbnVsbCwgIm1ldGEiOiB7fSwgImV4cCI6IDE2NjI1NDAyNjh9.8a1a3f2735e90bd3a8abd9615e7bc26e5860297968250268d371a31728c04556.7bbdrA5kQ06nAZP9ieEhTA.a1ttdUyxI3KdlcO1evA_Fyy1icAxQd8nXgGUlEThLoE'
        header, payload, signature, api_key, secret_key_hash = token.split('.')

        header_data = json.loads(base64.urlsafe_b64decode(header+'=='))

        if header_data.get('typ')=='v1':

            developer = models.user.developer.Developer.objects.get(api_key=api_key)

            secret_key_hash_bytes = hmac.new(settings.SECRET_KEY.encode(), msg=developer.secret_key.encode(), digestmod=hashlib.sha256).digest()
            _secret_key_hash = base64.urlsafe_b64encode(secret_key_hash_bytes).rstrip(b'=').decode('utf-8')
            print(_secret_key_hash)
            print(secret_key_hash)
        else:
            print('error')

    async def test_tiktok(self):
        # import service
        # room_id = 7145677881782455067
        # success, data = service.tiktok.live.send_message('testing',room_id, session_id = '48916791f979823f6aea8806a980110a')
        # print(success)
        # print(data)


        # return
        from TikTokLive import TikTokLiveClient
        from TikTokLive.types.events import CommentEvent, ConnectEvent
        client: TikTokLiveClient = TikTokLiveClient(unique_id="@handsome1105")

        await client.send_message('hi how are you',session_id='48916791f979823f6aea8806a980110a')
        print('done')
        # Instantiate the client with the user's username
    #     client: TikTokLiveClient = TikTokLiveClient(unique_id="@caishangkun",**(
    #     {

    #         # Custom Asyncio event loop
    #         "loop": None,

    #         # Custom Client params
    #         "client_params": {},

    #         # Custom request headers
    #         "headers": {},

    #         # Custom timeout for Webcast API requests
    #         "timeout_ms": 20000,

    #         # How frequently to make requests the webcast API when long polling
    #         "ping_interval_ms": 1000,

    #         # Whether to process initial data (cached chats, etc.)
    #         "process_initial_data": True,

    #         # Whether to get extended gift info (Image URLs, etc.)
    #         "enable_extended_gift_info": True,

    #         # Whether to trust environment variables that provide proxies to be used in http requests
    #         "trust_env": False,

    #         # A dict object for proxies requests
    #         # "proxies": {
    #         #     "http://": "http://username:password@localhost:8030",
    #         #     "https://": "http://420.69.420:8031",
    #         # },

    #         # Set the language for Webcast responses (Changes extended_gift's language)
    #         "lang": "en-US",

    #         # Connect info (viewers, stream status, etc.)
    #         "fetch_room_info_on_connect": True,

    #         # Whether to allow Websocket connections
    #         "websocket_enabled": False,
            
    #         # Parameter to increase the amount of connections made per minute via a Sign Server API key. 
    #         # If you need this, contact the project maintainer.
    #         "sign_api_key": None

    #     }
    # ))


    #     # Define how you want to handle specific events via decorator
        # @client.on("connect")
        # async def on_connect(_: ConnectEvent):
        #     print("Connected to Room ID:", client.room_id)


    #     # # Notice no decorator?
    #     # async def on_comment(event: CommentEvent):
    #     #     print(f"{event.user.nickname} -> {event.comment}")


    #     # # Define handling an event via "callback"
    #     # client.add_listener("comment", on_comment)
        # try:
        # client.run(session_id='48916791f979823f6aea8806a980110a')
        # except Exception:
        #     import traceback
        #     print(traceback.format_exc())
        # client.run()
        # data = client.send_message('1234', session_id='48916791f979823f6aea8806a980110a')
        # print(data)

    def test_temp(self):
        from database.lss._config import db

        products = db.api_product.find({"user_subscription_id":617})
        for product in products:
            ordr_startr_id = product.get('meta',{}).get('ordr_startr_id')
            db.api_product.update_one({'id':product.get('id')},{"$set":{"meta":{'ordr_startr':{'ordr_startr_id':ordr_startr_id}}}})
            # print(product.get('meta'))
    def test_ordr_startr(self):
        from plugins.ordr_startr import service as ordr_startr_service

        success, data = ordr_startr_service.product.get_products('ordrstartr2022!')
        print(success)
        print(data)

        
    def test_cache_redis(self):
        from pprint import pprint

        import pottery

        import database

        # database.lss_cache.redis.delete('default')
        campaign_products = database.lss_cache.campaign_product.get_products_all(1211, bypass=True)
        print(campaign_products)
        # @pottery.redis_cache(redis=database.lss_cache.redis, key='default')
        # def test(key=None):
        #     print('in')
        #     return 1

        # print(test(key='b'))
        # print(test.cache_info())
    # return collection.filter(**kwargs)
        # database.lss_cache.campaign_product.invalidate(1162,'ordr_startr','external_internal_map')
        # success, data, lock = database.lss_cache.campaign_product.leash_get_external_internal_map(1165,'ordr_startr')
        # print(success)
        # if not success:
        #     with lock:
        #         data = {'a':1}
        #         database.lss_cache.campaign_product.set_external_internal_map(1165, 'ordr_startr', data)

        
        # print(data)
        # data = database.lss_cache.campaign_product.get_products_all(1211)
        # pprint(data)
        # success, data, lock = database.lss_cache.campaign_product.leash_get_products_for_sell(1211)
        # print(success)
        # print(data)


        # if not success and lock:
        #     with lock:
        #         data = [json.loads({'a':1})]
        #         database.lss_cache.campaign_product.set_products_for_sell(1211, data)
        # print(success)
        # print(data)


    def test_shopify(self):
        from pprint import pprint

        from api import models
        from automation import jobs
        from plugins.shopify.service.checkouts import create_checkout


        user_subscription = models.user.user_subscription.UserSubscription.objects.get(id=566)
        c = user_subscription.user_plan.get('plugins').get('shopify')
        print(c)
        # line_items=[{'variant_id':41928314388671,'quantity':1}]

        # success,data = create_checkout(c.get('shop'),c.get('store_front_token'),line_items,0)
        # pprint(data)
        # campaign_id = 
        # c= {
        #     "shop": "frog-sweat-home.myshopify.com",
        #     "access_token": "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"
        # }
        data = jobs.shopify.export_product_job(user_subscription.id,c)
        pprint(data)
        # print(len(data.get('products')))
        # data = jobs.shopify.export_order_job(1193,c)
        # print(len(data.get('orders')))
        # pprint(data)
    def test_easy_store(self):
        from pprint import pprint

        from api import models
        from automation import jobs

        user_subscription = models.user.user_subscription.UserSubscription.objects.get(id=618)
        c = user_subscription.user_plan.get('plugins').get('easy_store')
        print(c)
        campaign_id = 1198
        jobs.easy_store.export_order_job(campaign_id, c)


    def test_facebook_messenger(self):

        import service
        token = 'EAANwBngXqOABAG2i9ZAsCqFZCMz9Wykmd43JbZAzEIgnZCYszZCcxhnSkw4rTvTO8KCdMbXt3P1IIiF7KmvIBbgLGR4N8QwiXO9AOCzfumh3v95yfFJgOBNhqo3O71MkwZAl2ZAJJoxTi3MoBs0JMdFVTTuKD0LqZCPmdPPOiWvlLFZAhZBXsvvlPTdbPkIDJEDAEZD'

        psid = "4422762234485468" 

        attachment={
            "type":"template",
            "payload":{
                "template_type":"button",
                "text":"What do you want to do next?",
                "buttons":[
                {
                    "type":"web_url",
                    "url":"https://www.messenger.com",
                    "title":"Visit Messenger"
                }]
            }
        }
        a,b = service.facebook.message.send_private_message(token,psid,'hi', attachment = attachment)
        print(a)
        print(b)
    
    def test_get_facebook_app_secret_proof(self):
        import hashlib
        import hmac

        page_token = 'EAANwBngXqOABAAOHBdSPAZAWckuo6imoCtBHH8c26aAhZASsIGv9VBvaMuy7pb1lrpieSZASIkC5fQAQoxgPsnpeVRkG4KF5bsSvzmVJimvhxfVIGgcXEA3JdHkyYyZCenGYYeChEaZCWSeL9TK7e60uRU7GdxZAYtRTl4FTftSRvBf3Yg3Mr129Dc0ZA4MnMqlegX0oiAkKWUWriE1Ifzs1XUQUJeUxNkZD'
        app_secret='e36ab1560c8d85cbc413e07fb7232f99'
        app_secret_proof = hmac.new(app_secret.encode(), msg=page_token.encode(), digestmod=hashlib.sha256).hexdigest()
        print(app_secret_proof)

    def create_cart_base_on_pre_order(self):
        import database
        from api import models


        pre_orders = models.order.pre_order.PreOrder.objects.all()


        for pre_order in pre_orders:
            try:
                models.cart.cart.Cart.objects.create(
                    campaign = pre_order.campaign if hasattr(pre_order, 'campaign') else None,
                    customer_id = pre_order.customer_id if hasattr(pre_order, 'customer_id') else None,
                    customer_name = pre_order.customer_name if hasattr(pre_order, 'customer_name') else "",
                    customer_img = pre_order.customer_img if hasattr(pre_order, 'customer_img') else None,

                    platform = pre_order.platform if hasattr(pre_order, 'platform') else "",
                    platform_id = pre_order.platform_id if hasattr(pre_order, 'platform_id') else None,
                    
                    products = {key:value.get('qty',0)for key, value in pre_order.products.items()},

                    lock_at = pre_order.lock_at if hasattr(pre_order, 'lock_at') else None,

                    adjust_title = pre_order.adjust_title if hasattr(pre_order, 'adjust_title') else "",
                    adjust_price = pre_order.adjust_price if hasattr(pre_order, 'adjust_price') else 0,
                    
                    free_delivery = pre_order.free_delivery if hasattr(pre_order, 'free_delivery') else False,

                    buyer = pre_order.buyer if hasattr(pre_order, 'buyer') else None,

                    discount = pre_order.discount if hasattr(pre_order, 'discount') else 0,
                    applied_discount = pre_order.applied_discount if hasattr(pre_order, 'applied_discount') else {},
                    
                    tax = pre_order.tax if hasattr(pre_order, 'tax') else 0,

                    meta = pre_order.meta if hasattr(pre_order, 'meta') else {},
                )
            except Exception:
                continue
            
    def handle_new_registeration_from_hubspot(self):

        # Verify.is_hubspot_signature_valid(request)
        # vid, = lib.util.getter.getdata(request,('vid',)) 
        # first_name, last_name, email, subscription_type, country_code, phone = \
        #     lib.util.getter.getproperties(request.data.get('properties'),('firstname','lastname','email','subscription_type','country_code','phone'), nest_property='value')

        # country = lib.util.country_mapping.country_code_to_country.get(country_code,'SG')
        password = ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(8))
        

        # rule.check_rule.user_check_rule.UserCheckRule.has_email_been_registered_as_seller(email=email)

        # now = datetime.now() 
        # expired_at = now+datetime.timedelta(days=90)
        email = "dermaskinshop.my@gmail.com"
        if AuthUser.objects.filter(email=email).exists():
            auth_user = AuthUser.objects.get(email=email)
            # set new password
            auth_user.set_password(password)
            auth_user.save()

        # else:
        #     auth_user = AuthUser.objects.create_user(
        #         username=f'{first_name} {last_name}', email=email, password=password)
        

        # user_subscription = models.user.user_subscription.UserSubscription.objects.create(
        #     name=f'{first_name} {last_name}', 
        #     status='new', 
        #     started_at=now,
        #     expired_at=expired_at, 
        #     user_plan= {"activated_platform" : ["facebook", "instagram", "youtube"]}, 
        #     meta_country={ 'activated_country': [country] },
        #     type=business_policy.subscription.TYPE_TRIAL,

        #     lang=country_plan.language ,
        #     country = country
        #     )
        api_user = models.user.user.User.objects.get(email=email)
        first_name = "Dermaskinshop"
        user_subscription = api_user.user_subscription
        subscription_type = user_subscription.type
        country = user_subscription.country
        country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(country)
        # api_user = models.user.user.User.objects.create(name=f'{first_name} {last_name}', 
        #     email=email, type='user', 
        #     status='valid', 
        #     phone=country_code+phone, 
        #     auth_user=auth_user, 
        #     user_subscription=user_subscription)
        
        # record_subscription_for_trial_user(user_subscription, api_user)
        
        # lib.util.marking_tool.NewUserMark.mark(api_user, save = True)
        # marketing_plans = MarketingPlan.get_plans("current_plans")
        # for key, val in marketing_plans.items():
        #     if key == "welcome_gift":
        #         lib.util.marking_tool.WelcomeGiftUsedMark.mark(api_user, save = True, mark_value=False)
        #         PromotionCode.objects.create(
        #             name=key,
        #             api_user=api_user,
        #             user_subscription=user_subscription,
        #         )
        
        # service.hubspot.contact.update(vid,expiry_date=int(expired_at.replace(hour=0,minute=0,second=0,microsecond=0).timestamp()*1000))
        service.sendinblue.contact.create(email=email,first_name=first_name, last_name=last_name)
        service.sendinblue.transaction_email.AccountActivationEmail(first_name, subscription_type, email, password, to=[email], cc=country_plan.cc).send()
        print("ok")
        return Response("ok", status=status.HTTP_200_OK)




    def test_import_account(self):

        from automation import jobs

        jobs.import_account_job.imoprt_account_job('Till End OCT2022.xlsx','1')

    def test_add_user_subscription_to_order(self):
        import traceback

        from api import models

        # for cart in models.cart.cart.Cart.objects.filter(user_subscription=None):
        #     try:
        #         print(cart.id)
        #         cart.user_subscription = cart.campaign.user_subscription
        #         cart.save()       
        #     except Exception:
        #         print(traceback.format_exc())
        offset = 16000
        for i, order in enumerate(models.order.order.Order.objects.all()[offset:offset+8000]):
        # for order in models.order.order.Order.objects.filter(user_subscription=None)[:8000]:
            try:
                print(offset+i)

                order.price_unit = order.campaign.price_unit
                order.decimal_places = order.campaign.decimal_places
                order.currency = order.campaign.currency

                order.save()       
            except Exception:
                print(traceback.format_exc())
    
    def test_cart_expired_adjustment(self):
        import traceback
        import database
        from api import models

        # data = database.lss.order.get_wallet_with_expired_points()
        data = database.lss.order.get_used_expired_points_sum(673, 1)
        print(data)