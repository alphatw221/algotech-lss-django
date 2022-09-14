import os
import config
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception as e:
    pass


from plugins.shopify import service as shopify_service
from plugins.shopify import lib as shopify_lib
from api import models

import traceback
import database

PLUGIN_SHOPIFY = 'shopify'

def export_product_job(user_subscription_id, credential):
    try:
        user_subscription = models.user.user_subscription.UserSubscription.objects.get(id=user_subscription_id)
        product_categories:list = user_subscription.meta.get('product_categories',[])

        product_dict = {product.meta.get(PLUGIN_SHOPIFY,{}).get('variant_id') : product.id for product in user_subscription.products.all() if product.meta.get(PLUGIN_SHOPIFY,{}).get('variant_id')}
        tag_set:set = set(product_categories) 

        success, data = shopify_service.products.get_published_product(credential.get('shop'), credential.get('access_token'))

        if not success:
            raise Exception()
        
        for product in data.get('products'):
            product_id = product.get('id')

            tags = product.get('tags').split(',')
            # if tags:
            for tag in tags:
                if tag not in tag_set:
                    product_categories.append(tag)
                    tag_set.add(tag)


            for variant in product.get('variants'):
                lss_product_data = shopify_lib.transformer.to_lss_product(product, variant, user_subscription, tags)
                variant_id = variant.get('id')
                variant_name = variant.get('name')

                meta_data = {
                    'shopify': {
                        "product_id": product_id,
                        "variant_id": variant_id,
                        "variant_name": variant_name,
                    }
                }

                if variant_id in product_dict:
                    lss_product_id = product_dict[variant_id]
                    models.product.product.Product.objects.filter(id=lss_product_id).update(**lss_product_data)
                else:
                    models.product.product.Product.objects.create(**lss_product_data, meta = meta_data)

        user_subscription.save()

        shopify_service.channels.export_product.send_result_data(user_subscription.id,{'result':'complete'})
    except Exception:
        print(traceback.format_exc())
        shopify_service.channels.export_product.send_result_data(user_subscription_id,{'result':'fail'})

  
STATUS_PROCEED = 'proceed'
STATUS_COMPLETE = 'complete'
STATUS_REVIEW = 'review'
STATUS_SHIPPING_OUT = 'shipping out'
STATUS_EXPIRED = 'expired'
STATUS_PENDING_REFUND = 'pending_refund'

def export_order_job(campaign_id, credential):
    try:
        campaign = models.campaign.campaign.Campaign.objects.get(id=campaign_id)

        shopify_order_dict = {str(order.meta.get(PLUGIN_SHOPIFY,{}).get('id')):order.id for order in campaign.orders.all() if order.meta.get(PLUGIN_SHOPIFY,{}).get('id')}
        campaign_product_external_internal_map = shopify_lib.mapping_helper.CampaignProduct.get_external_internal_map(campaign)
        since = campaign.start_at.strftime("%Y-%m-%d %H:%M:%S")
        
        success, data = shopify_service.orders.list_order(
            credential.get('shop'), 
            credential.get('access_token'), 
            created_at_min=since
            )


        if not success:
            raise Exception()
        

        for order in data.get('orders'):
            try:
                if order.get('financial_status')!='paid':   #shopify status no paid
                    continue
            
                landing_site = order.get('landing_site','')
                if not landing_site:
                    continue
                
                order_key = landing_site[-32:]
                
                if order_key not in campaign.meta:
                    continue
                lss_pre_order_id = campaign.meta[order_key]
                lss_pre_order = models.order.pre_order.PreOrder.objects.get(id=lss_pre_order_id)

                lss_order_data=shopify_lib.transformer.to_lss_order(lss_pre_order, order, campaign_product_external_internal_map)

                if str(order.get('id')) in shopify_order_dict:
                    continue

                lss_order = models.order.order.Order.objects.create(**lss_order_data)

                for campaign_product_id_str, product in lss_order.products.items():
                    database.lss.campaign_product.CampaignProduct(id = int(campaign_product_id_str)).sold_from_external(product.get('qty'), sync=False) 

                for campaign_product_id_str, product in lss_pre_order.products.items():
                    database.lss.campaign_product.CampaignProduct(id = int(campaign_product_id_str)).customer_return(product.get('qty'), sync=False) #do this anyway
                database.lss.pre_order.PreOrder(id=lss_pre_order.id).reset_pre_order(sync=False)        #do this anyway
                database.lss.order_product.OrderProduct.transfer_to_order(lss_pre_order, lss_order)     #do this anyway


            except Exception as e:
                print(traceback.format_exc())
                continue
        
        shopify_service.channels.export_order.send_result_data(campaign.id,{'result':'complete'})
    except Exception:
        print(traceback.format_exc())
        shopify_service.channels.export_order.send_result_data(campaign.id,{'result':'fail'})