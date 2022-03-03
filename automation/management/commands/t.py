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
from backend.comment_catching.facebook.post_comment import *
from django.core.management.base import BaseCommand
from api.views.order.order_report import *
from backend.pymongo.mongodb import db, get_incremented_filed
from automation.jobs.campaign_job import *
from backend.api.instagram.user import *
from backend.api.youtube.viedo import api_youtube_get_video_info_with_api_key, api_youtube_get_video_comment_thread
from automation.jobs.campaign_job import campaign_job
from mail.sender.sender import *
from api.views.payment.payment import * 

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.product.product import Product
from api.models.order.order import Order
from api.models.order.order_product import OrderProduct
import datetime


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

        self.convert_arimme()

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
    
    def convert_arimme(self):
        import pymysql
        mysql_hostname, mysql_port, mysql_dbname = '34.124.188.130', 3306, 'lss'
        mysql_user, mysql_password = 'root', 'algo83111T%%'

        conn = pymysql.connect(host=mysql_hostname, database=mysql_dbname, user=mysql_user, passwd=mysql_password, port=mysql_port, charset='utf8')
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor1 = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor2 = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor3 = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor4 = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor5 = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor6 = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor7 = conn.cursor(cursor=pymysql.cursors.DictCursor)
        cursor8 = conn.cursor(cursor=pymysql.cursors.DictCursor)
        
        sql6 = 'select * from lss_fb_page_meta where fb_page_id="528158520664119"'

        ## -------- insert product
        # sql7 = 'SELECT * FROM lss_product WHERE fb_user_id IN ("468936317671599", "10159642927732044")'
        # cursor7.execute(sql7)
        # arimee_products = cursor7.fetchall()
        # for pro in arimee_products:
        #     product_id = pro['product_id']
        #     type = pro['product_type'] 
        #     qty = pro['quantity'] 
        #     price = pro['price'] 
        #     image = pro['image'] 
        #     created_at = pro['date_added'] 
        #     updated_at = pro['date_modified'] 
        #     status = 'enabled'
        #     user_subscription_id = 2
        #     created_by_id = 66

        #     name, description, order_code = '', '', ''
        #     sql8 = 'select * from lss_product_description where product_id=' + str(product_id)
        #     cursor8.execute(sql8)
        #     prodcut_metas = cursor8.fetchall()
        #     for meta in prodcut_metas:
        #         name = meta['name']
        #         description = meta['description']
        #         order_code = meta['order_code']

        #     prod = Product.objects.create(
        #         user_subscription_id=user_subscription_id, created_by_id=created_by_id, qty=qty,
        #         name=name, description=description, price=price, image=image, order_code=order_code,
        #         type=type, status=status, created_at=created_at, updated_at=updated_at
        #     )
        #     prod.save()


        

        ## ----------- insert api_campaign
        lss_campaign_command = 'select * from lss_fb_campaign where fb_page_id="528158520664119"'
        cursor.execute(lss_campaign_command)
        arimee_campaigns = cursor.fetchall()

        for campaign in arimee_campaigns:
            old_campaign_id = campaign['fb_campaign_id']

            campaign = Campaign.objects.create(
                title=campaign['title'], 
                description=campaign['description'], 
                created_at=campaign['date_added'], 
                updated_at=campaign['date_added'], 
                facebook_campaign={"post_id":campaign['fb_post_id']}, 
                facebook_page_id=25, 
                created_by_id=66, 
                status='new')

            lss_campaign_product_command = 'select * from lss_fb_campaign_product where fb_campaign_id=' + str(old_campaign_id)
            cursor.execute(lss_campaign_product_command)
            sql_campaign_products = cursor.fetchall()

            campaign_product_mapping={}
            for sql_campaign_product in sql_campaign_products:

                campaign_product = CampaignProduct.objects.create(
                    campaign=campaign, 
                    qty_for_sale=sql_campaign_product['product_quantity'], 
                    name=sql_campaign_product['name'], 
                    order_code=sql_campaign_product['order_code'], 
                    max_order_amount=sql_campaign_product['max_order_amount'], 
                    type=sql_campaign_product['product_type'], 
                    created_by_id=66)
                
                campaign_product_mapping[sql_campaign_product['product_id']]=campaign_product.id
            
            ## ----------- insert api_order--------------------------------------------------------------
            lss_order_command = 'select * from lss_order where campaign_id=' + str(old_campaign_id)
            cursor1.execute(lss_order_command)
            sql_orders = cursor1.fetchall()

            for sql_order in sql_orders:

                order_id = sql_order['id']
                order_status = 'complete' if sql_order['order_status'] == 'process' else 'review'
                total = sql_order['total']
                customer_id = sql_order['fb_user_id']
                customer_name = sql_order['fb_user_name']
                image = sql_order['image']
                created_at = sql_order['created_time']
                updated_at = sql_order['modified_time']
                platform, platform_id = 'facebook', 1
                
                lss_order_meta_command = 'select * from lss_order_meta where order_id=' + str(order_id)
                cursor2.execute(lss_order_meta_command)
                subtotal, payment_method, payment_info, delivery_charge = 0, '', '', 0
                modify_total, modify_total_remarks, free_delivery_by_campaign_admin = 0, '', False
                sql_order_metas= cursor2.fetchall()
                for sql_order_meta in sql_order_metas:
                    if sql_order_meta['meta_key'] == 'subtotal':
                        subtotal = float(sql_order_meta.get('meta_value', "0")) if sql_order_meta.get('meta_value') else 0
                    if sql_order_meta['meta_key'] == 'payment_method':
                        payment_method = sql_order_meta.get('meta_value','')
                    if sql_order_meta['meta_key'] == 'payment_info':
                        payment_info = sql_order_meta.get('meta_value','')

                    if sql_order_meta['meta_key'] == 'delivery_charge':
                        delivery_charge = float(sql_order_meta.get('meta_value',"0")) if sql_order_meta.get('meta_value') else 0
                    if sql_order_meta['meta_key'] == 'modify_total':
                        modify_total = float(sql_order_meta.get('meta_value',"0")) if sql_order_meta.get('meta_value') else 0
                    if sql_order_meta['meta_key'] == 'modify_total_remarks':
                        modify_total_remarks = sql_order_meta.get('meta_value','')
                    if sql_order_meta['meta_key'] == 'free_delivery_by_campaign_admin':
                        free_delivery_by_campaign_admin = True if sql_order_meta.get('meta_value')=="true" else False


                shipping_first_name, shipping_last_name, shipping_phone, shipping_email = '', '', '', ''
                shipping_post_code, shipping_address, delivery_way, shipping_remarks, shipping_date = '', '', '', '', None
                sql3 = 'select * from lss_order_user_meta where order_id=' + str(order_id)
                cursor3.execute(sql3)
                user_metas = cursor3.fetchall()

                for user_meta in user_metas:
                    if user_meta['meta_key'] == 'shipping_first_name':
                        shipping_first_name = user_meta['meta_value']
                    if user_meta['meta_key'] == 'shipping_last_name':
                        shipping_last_name = user_meta['meta_value']
                    if user_meta['meta_key'] == 'shipping_phone':
                        shipping_phone = user_meta['meta_value']
                    if user_meta['meta_key'] == 'shipping_email':
                        shipping_email = user_meta['meta_value']
                    if user_meta['meta_key'] == 'shipping_post_code':
                        shipping_post_code = user_meta['meta_value']
                    if user_meta['meta_key'] == 'shipping_address':
                        shipping_address = user_meta['meta_value']
                    if user_meta['meta_key'] == 'delivery_way':
                        delivery_way = user_meta['meta_value']
                    if user_meta['meta_key'] == 'shipping_remarks':
                        shipping_remarks = user_meta['meta_value']
                    if user_meta['meta_key'] == 'shipping_date':
                        shipping_date = user_meta['meta_value'][:10] if user_meta['meta_value'] else None
                    if user_meta['meta_key'] == 'delivery_way':
                        delivery_way = user_meta['meta_value']
                
            
                order = Order.objects.create(
                    campaign=campaign, customer_id=customer_id, customer_name=customer_name, customer_img=image,
                    shipping_first_name=shipping_first_name, shipping_last_name=shipping_last_name,
                    shipping_email=shipping_email, shipping_phone=shipping_phone, shipping_postcode=shipping_post_code,
                    shipping_address_1=shipping_address, shipping_method=delivery_way, shipping_remark=shipping_remarks,
                    shipping_date=shipping_date, platform=platform, platform_id=platform_id, status=order_status,
                    created_at=created_at, updated_at=updated_at, products={}, subtotal=subtotal, total=total, 
                    shipping_cost=delivery_charge, payment_method=payment_method, free_delivery=free_delivery_by_campaign_admin,
                    adjust_price=modify_total, adjust_title=modify_total_remarks
                )

                sql4 = 'select * from lss_order_product where order_id=' + str(order_id)
                cursor4.execute(sql4)
                user_products = cursor4.fetchall()

                
                products={}
                for user_product in user_products:
                    try:
                        order_product = OrderProduct.objects.create(
                            campaign=campaign, campaign_product=CampaignProduct.objects.get(id=campaign_product_mapping[user_product['product_id']]), order=order,
                            name=user_product['name'], price=user_product['price'], qty=user_product['quantity'],
                            subtotal=user_product['total']
                        )

                        products[str(order_product.id)]={
                            "campaign_product_id":order_product.campaign_product.id,
                            "name":order_product.name,
                            # "image":order_product.image,
                            "price":order_product.price,
                            "type":order_product.type,
                            "currency" : None,
                            # "currency_sign" : order_product,
                            "qty" : order_product.qty,
                            "subtotal" : order_product.subtotal
                        }
                    except: 
                        pass
                print(products)
                order.products=products
                order.save()

        

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