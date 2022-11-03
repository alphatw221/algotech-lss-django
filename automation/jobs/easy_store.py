from operator import mod
import os
import config
import django
import database
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception as e:
    pass


from plugins.easy_store import service as easy_store_service
from plugins.easy_store import lib as easy_store_lib
from api import models

import traceback

PLUGIN_EASY_STORE = 'easy_store'

def export_product_job(user_subscription_id, credential):
    try:

        user_subscription = models.user.user_subscription.UserSubscription.objects.get(id=user_subscription_id)
        product_categories_dict = {product_category.name:product_category.id for product_category in user_subscription.product_categories.all()}

        models.product.product.Product.objects.filter(user_subscription=user_subscription).delete()
        product_dict = {product.meta.get(PLUGIN_EASY_STORE,{}).get('variant_id') : product.id for product in user_subscription.products.all() if product.meta.get(PLUGIN_EASY_STORE,{}).get('variant_id')}

        page = 1
        page_count = 1
        while(page_count>=page):
            success, data = easy_store_service.products.get_published_product(credential.get('shop'), credential.get('access_token'),page=page)
            
            if not success:
                raise Exception()
            
            page_count = data.get('page_count')

            for product in data.get('products'):
                product_id = product.get('id')

                categories = []
                for collection in product.get('collections'):
                    collection_name = collection.get('name')
                    if not collection_name:
                        continue
                    if collection_name not in product_categories_dict:
                        try: 
                            product_category = models.product.product_category.ProductCategory.objects.create(
                                user_subscription=user_subscription,
                                name = collection_name
                            )
                            product_categories_dict[product_category.name] = product_category.id
                            categories.append(str(product_category.id))
                        except Exception:
                            pass #duplicate key 
                    else:
                        categories.append(str(product_categories_dict.get(collection_name)))

                for variant in product.get('variants'):

                    lss_product_data = easy_store_lib.transformer.to_lss_product(product,variant, user_subscription, categories)
                    variant_id = variant.get('id')
                    variant_name = variant.get('name')

                    meta_data = {'easy_store':{
                            "product_id":product_id,
                            "variant_id":variant_id,
                            "variant_name":variant_name,
                        }}
                    if variant_id in product_dict:
                        lss_product_id = product_dict[variant_id]
                        models.product.product.Product.objects.filter(id=lss_product_id).update(**lss_product_data)
                    else:
                        models.product.product.Product.objects.create(**lss_product_data,meta = meta_data)

            page+=1
        
        easy_store_service.channels.export_product.send_result_data(user_subscription.id,{'result':'complete'})
    except Exception:
        print(traceback.format_exc())
        easy_store_service.channels.export_product.send_result_data(user_subscription_id,{'result':'fail'})


# STATUS_PROCEED = 'proceed'
# STATUS_COMPLETE = 'complete'
# STATUS_REVIEW = 'review'
# STATUS_SHIPPING_OUT = 'shipping out'
# STATUS_EXPIRED = 'expired'
# STATUS_PENDING_REFUND = 'pending_refund'

def export_order_job(campaign_id, credential):
    try:
        campaign = models.campaign.campaign.Campaign.objects.get(id=campaign_id)

        order_external_internal_map = {str(order.meta.get(PLUGIN_EASY_STORE,{}).get('id')):order.id for order in campaign.orders.all() if order.meta.get(PLUGIN_EASY_STORE,{}).get('id')}
        campaign_product_external_internal_map = easy_store_lib.mapping_helper.CampaignProduct.get_external_internal_map(campaign)
        since = campaign.start_at.strftime("%Y-%m-%d %H:%M:%S")
        page = 1
        page_count = 1
        while(page_count>=page):
            success, data = easy_store_service.orders.list_order(
            credential.get('shop'), 
            credential.get('access_token'), 
            created_at_min=since, 
            page=page)

            if not success:
                raise Exception()
            

            for easy_store_order in data.get('orders'):
                try:
                    cart_token = easy_store_order['cart_token']

                    if cart_token not in campaign.meta:
                        continue

                    if str(easy_store_order['id']) in order_external_internal_map:
                        continue

                    lss_cart_id = campaign.meta[cart_token]

                    lss_cart = models.cart.cart.Cart.objects.get(id = lss_cart_id)
                    
                    lss_order_data = easy_store_lib.transformer.to_lss_order(easy_store_order, lss_cart)
                    lss_order = models.order.order.Order.objects.create(**lss_order_data)

                    order_products_data = easy_store_lib.transformer.to_lss_order_products(easy_store_order, lss_order, campaign_product_external_internal_map)
                    for order_product_data in order_products_data:
                        models.order.order_product.OrderProduct.objects.create(**order_product_data)
  
                    for campaign_product_id_str, qty in lss_order.products.items():
                        database.lss.campaign_product.CampaignProduct(id = int(campaign_product_id_str)).sold_from_external(qty, sync=False) 

                    for campaign_product_id_str, qty in lss_cart.products.items():
                        database.lss.campaign_product.CampaignProduct(id = int(campaign_product_id_str)).customer_return(qty, sync=False) #do this anyway

                    database.lss.cart.Cart(id=lss_cart_id).clear(sync=False) 


                except Exception as e:
                    print(traceback.format_exc())
                    continue

            page_count = data.get('page_count')
            page+=1
        
        easy_store_service.channels.export_order.send_result_data(campaign.id,{'result':'complete'})
    except Exception:
        print(traceback.format_exc())
        easy_store_service.channels.export_order.send_result_data(campaign.id,{'result':'fail'})