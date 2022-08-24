import os
import config
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception as e:
    pass


from plugins.easy_store import service as easy_store_service
from api import models

import traceback

def export_product_job(user_subscription_id, credential):
    try:
  
        user_subscription = models.user.user_subscription.UserSubscription.objects.get(id=user_subscription_id)
        product_categories:list = user_subscription.meta.get('product_categories',[])

        sku_dict = { product.sku:product.id  for product in user_subscription.products.all() if product.sku}
        tag_set:set = set(product_categories) 
        

        page = 1
        page_count = 1
        while(page_count>=page):
            success, data = easy_store_service.products.get_published_product(credential.get('shop'), credential.get('access_token'),page=page)
            
            if not success:
                raise Exception()
            
            page_count = data.get('page_count')


            for product in data.get('products'):
                product_id = product.get('id')
                name = product.get('name')
                image_url = product.get('images')[0].get('url') if product.get('images') else  ''
                description = product.get('description')

                tags = []
                for collection in product.get('collections'):
                    collection_name = collection.get('name')
                    if not collection_name:
                        continue
                    if collection_name not in tag_set:
                        product_categories.append(collection_name)
                        tag_set.add(collection_name)
                    tags.append(collection_name)

                for variant in product.get('variants'):
                    
                    sku = variant.get('sku')
                    variant_id = variant.get('id')
                    variant_name = variant.get('name')
                    price = variant.get('price')
                    qty = variant.get('inventory_quantity')

                    meta_data = {'easy_store':{
                            "product_id":product_id,
                            "variant_id":variant_id,
                            "variant_name":variant_name,
                            "image":image_url
                        }}
                    if sku in sku_dict:
                        lss_product = models.product.product.Product.objects.get(id=sku_dict[sku])
                        lss_product.price = price
                        lss_product.name = name
                        lss_product.description = description
                        lss_product.tag = tags
                        lss_product.qty = qty
                        lss_product.status = models.product.product.STATUS_ENABLED
                        lss_product.meta.update(meta_data)
                        lss_product.save()
                    else:
                        models.product.product.Product.objects.create(
                            user_subscription = user_subscription, name = name, price=price, sku=sku, tag=tags, qty = qty, status = models.product.product.STATUS_ENABLED, meta=meta_data, description=description)

            page+=1

        user_subscription.save()
        
        easy_store_service.channels.export_product.send_result_data(user_subscription.id,{'result':'complete'})
    except Exception:
        print(traceback.format_exc())
        easy_store_service.channels.export_product.send_result_data(user_subscription_id,{'result':'fail'})


STATUS_PROCEED = 'proceed'
STATUS_COMPLETE = 'complete'
STATUS_REVIEW = 'review'
STATUS_SHIPPING_OUT = 'shipping out'
STATUS_EXPIRED = 'expired'
STATUS_PENDING_REFUND = 'pending_refund'

def export_order_job(campaign_id, credential):
    try:
        campaign = models.campaign.campaign.Campaign.objects.get(id=campaign_id)

        easy_store_order_dict = {str(order.meta.get('easy_store',{}).get('id')):order.id for order in campaign.orders.all() if order.meta.get('easy_store',{}).get('id')}

        since = campaign.start_at.strftime("%Y-%m-%d %H:%M:%S")
        page = 1
        page_count = 1
        while(page_count>=page):
            success, data = easy_store_service.orders.list_order(credential.get('shop'), credential.get('access_token'), 
            created_at_min=since, 
            page=page)
            
            if not success:
                raise Exception()
            

            for order in data.get('orders'):
                try:
                    cart_token = order['cart_token']
                    if cart_token not in campaign.meta:
                        continue
                    pre_order_id = campaign.meta[cart_token]
                    pre_order = models.order.pre_order.PreOrder.objects.get(id=pre_order_id)

                    if str(order['id']) in easy_store_order_dict:
                        lss_order_id = easy_store_order_dict[str(order['id'])]
                        lss_order = models.order.order.Order.objects.get(id=lss_order_id)

                        lss_order.status = models.order.order.STATUS_COMPLETE if order['financial_status']=='paid' else models.order.order.STATUS_REVIEW
                        lss_order.discount = float(order['total_discount'])
                        lss_order.subtotal = float(order['subtotal_price'])
                        lss_order.shipping_cost = float(order['total_shipping'])
                        lss_order.total = float(order['total_price'])
                        lss_order.products = {'easy_store':True}
                        lss_order.meta['easy_store']=order
                        lss_order.save()
                    else:
                        models.order.order.Order.objects.create(
                            campaign = campaign,
                            customer_id = pre_order.customer_id,
                            customer_name = pre_order.customer_name,
                            customer_img = pre_order.customer_img,
                            platform = pre_order.platform,
                            status = models.order.order.STATUS_COMPLETE if order['financial_status']=='paid' else models.order.order.STATUS_REVIEW,
                            discount = float(order['total_discount']),
                            subtotal = float(order['subtotal_price']),
                            shipping_cost = float(order['total_shipping']),
                            products = {'easy_store':True},
                            total = float(order['total_price']),

                            meta = {'easy_store':order}
                        )

                except Exception as e:
                    print(traceback.format_exc())
                    continue

            page_count = data.get('page_count')
            page+=1
        
        easy_store_service.channels.export_order.send_result_data(campaign.id,{'result':'complete'})
    except Exception:
        print(traceback.format_exc())
        easy_store_service.channels.export_order.send_result_data(campaign.id,{'result':'fail'})