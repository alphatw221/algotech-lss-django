from api import models
from django.conf import settings

def to_lss_product(shopify_product, shopify_variant_product, user_subscription, tags):
    
    data = {
        'name': shopify_product.get('title'),
        'image': shopify_product.get('images')[0].get('src') if shopify_product.get('images') else settings.GOOGLE_STORAGE_STATIC_DIR+models.product.product.IMAGE_NULL,
        'sku': shopify_variant_product.get('sku'),
        'price': float(shopify_variant_product.get('price')),
        'qty': int(shopify_variant_product.get('inventory_quantity')),
        'tag': tags,
        'description': shopify_product.get('body_html'),
        'user_subscription': user_subscription,
        'status': models.product.product.STATUS_ENABLED
    }

    return data


def to_lss_order(lss_pre_order, shopify_order_data, campaign_product_external_internal_map):

    lss_products = {}
    for item in shopify_order_data.get('line_items'):
        if item.get('variant_id') not in campaign_product_external_internal_map:
            continue
        campaign_product_data = campaign_product_external_internal_map[item.get('variant_id')]
        price = float(item.get('price'))
        qty = float(item.get('quantity'))
        subtotal = price*qty
        lss_products[str(campaign_product_data.get('id'))] = {
            "order_product_id":None,   #TODO
            "name":campaign_product_data.get('name'),
            "image":campaign_product_data.get('image'),
            "price":price,
            "type":campaign_product_data.get('type'),
            "qty":qty,
            "subtotal":subtotal
        }

    data = {
        "campaign" : lss_pre_order.campaign,
        "customer_id" : lss_pre_order.customer_id,
        "customer_name" : lss_pre_order.customer_name,
        "customer_img" : lss_pre_order.customer_img,
        "platform" : lss_pre_order.platform,
        "status" : models.order.order.STATUS_COMPLETE if shopify_order_data.get('financial_status')=='paid' else models.order.order.STATUS_REVIEW,
        "discount" : float(shopify_order_data.get('total_discounts')),
        "subtotal" : float(shopify_order_data.get('subtotal_price')),
        "shipping_cost" : float(shopify_order_data.get('total_shipping_price_set',{}).get('shop_money',{}).get('amount')),
        "payment_method" : shopify_order_data['payment_gateway_names'][0],
        
        "shipping_location" : shopify_order_data['shipping_address']['city'],
        "shipping_address_1" : shopify_order_data['shipping_address']['address1'],
        "shipping_postcode" : shopify_order_data['shipping_address']['zip'],
        "shipping_first_name" : shopify_order_data['shipping_address']['first_name'],
        "shipping_last_name" : shopify_order_data['shipping_address']['last_name'],
        "shipping_method" : "delivery",
        
        "products" : lss_products,
        "total" : float(shopify_order_data['total_price']),


        "meta" : {'shopify':shopify_order_data},
    }

    return data
