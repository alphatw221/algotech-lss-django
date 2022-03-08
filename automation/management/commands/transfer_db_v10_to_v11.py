from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.models.product.product import Product
from api.models.order.order import Order
from api.models.order.order_product import OrderProduct
from django.core.management.base import BaseCommand
import datetime
from backend.pymongo.mongodb import db


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.convert_arimme(7, 1, 4, '1679082475665513')
    

    def convert_arimme(self, fb_page_id, created_by_id, user_subscription_id, page_id):
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
        #     user_subscription_id = user_subscription_id
        #     created_by_id = created_by_id

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
        lss_campaign_command = 'select * from lss_fb_campaign where fb_page_id=' + page_id
        cursor.execute(lss_campaign_command)
        transfering_campaigns = cursor.fetchall()


        osc_title_list = []
        osc_campaigns = db.api_campaign.find({'created_by_id': 1})
        for osc_campaign in osc_campaigns:
            osc_title_list.append(osc_campaign['title'])

        for campaign in transfering_campaigns:
            old_campaign_id = campaign['fb_campaign_id']
            if campaign['title'] in osc_title_list:
                print ('poooop')
            else:
                campaign = Campaign.objects.create(
                    title=campaign['title'], 
                    description=campaign['description'], 
                    start_at=campaign['start_time'],
                    end_at=campaign['end_time'],
                    created_at=campaign['date_added'], 
                    updated_at=campaign['date_modified'], 
                    facebook_campaign={"post_id":campaign['fb_post_id']}, 
                    facebook_page_id=fb_page_id, 
                    created_by_id=created_by_id, 
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
                        created_by_id=created_by_id)
                    
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

                    shipping_first_name, shipping_last_name, shipping_phone, shipping_email, remark = '', '', '', '', ''
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
                            try:
                                shipping_date = datetime.datetime.strptime(shipping_date, '%y/%m/%d %H:%M:%S')
                            except:
                                shipping_date = None
                                remark = {'shipping_date': shipping_date}
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
                        adjust_price=modify_total, adjust_title=modify_total_remarks, remark=remark
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

                            products[str(order_product.campaign_product.id)]={
                                "order_product_id": order_product.id,
                                # "campaign_product_id":order_product.campaign_product.id,
                                "name":order_product.name,
                                # "image":order_product.image,
                                "price":order_product.price,
                                "type":order_product.type,
                                "currency" : None,
                                "currency_sign" : "$",
                                "qty" : order_product.qty,
                                "subtotal" : order_product.subtotal
                            }
                        except: 
                            pass
                    print(products)
                    order.products=products
                    order.save()





        # arimee_orders = db.api_order.find({'campaign_id': {'$in': [228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251]}})
        # for order in arimee_orders:
        #     products = order['products']
        #     order_id = order['id']

        #     new_products = {}
        #     for id, product in products.items():
        #         # campaign_product_id = product['campaign_product_id']
        #         # product['order_product_id'] = int(order_product_id)
        #         # product.pop('campaign_product_id')
        #         product['currency_sign'] = '$'
        #         # print (id, product)
        #         new_products[id] = product
            
        #     print (order_id)
        #     db.api_order.update({'id': order_id}, {'$set': {'products': new_products}})