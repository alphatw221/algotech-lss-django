from api import models
from django.conf import settings

def to_lss_product(easy_store_product, easy_store_variant_product, user_subscription, tags):

    
    data = {
        'name':easy_store_product.get('name'),
        'image':easy_store_product.get('images')[0].get('url') if easy_store_product.get('images') else  settings.GOOGLE_STORAGE_STATIC_DIR+models.product.product.IMAGE_NULL,
        'sku':easy_store_variant_product.get('sku'),
        'price':easy_store_variant_product.get('price'),
        'qty':easy_store_variant_product.get('inventory_quantity'),
        'tag':tags,
        'description':easy_store_product.get('description'),
        'user_subscription':user_subscription,
        'status':models.product.product.STATUS_ENABLED
    }

    return data


def to_lss_order(easy_store_order, lss_pre_order, campaign_product_dict):



    lss_products = {}
    for item in easy_store_order.get('line_items'):
        if item.get('variant_id') not in campaign_product_dict:
            continue
        campaign_product = campaign_product_dict[item.get('variant_id')]
        lss_products[str(campaign_product.id)] = {
            "order_product_id":None,   #TODO
            "name":campaign_product.name,
            "image":campaign_product.image,
            "price":float(item.get('price')),
            "type":campaign_product.type,
            "qty":float(item.get('quantity')),
            "subtotal":float(item.get('subtotal'))
        }


    data = {
        "campaign":lss_pre_order.campaign,
        "customer_id" : lss_pre_order.customer_id,
        "customer_name" : lss_pre_order.customer_name,
        "customer_img" : lss_pre_order.customer_img,
        "platform" : lss_pre_order.platform,
        "status" : models.order.order.STATUS_COMPLETE if easy_store_order.get('financial_status')=='paid' else models.order.order.STATUS_REVIEW,
        "discount" : float(easy_store_order.get('total_discount',0)),
        "subtotal" : float(easy_store_order.get('subtotal_price',0)),
        "shipping_cost" : float(easy_store_order.get('total_shipping',0)),
        "total" : float(easy_store_order.get('total_price',0)),
        "meta" : {'easy_store':easy_store_order},

        "products":lss_products

    }




                            
                            
                           



    return data

