from api import models
from django.conf import settings
import database

def to_lss_product(easy_store_product, easy_store_variant_product, user_subscription, tags):
    product_image = easy_store_product.get('images')[0].get('url') if easy_store_product.get('images') else  settings.GOOGLE_STORAGE_STATIC_DIR+models.product.product.IMAGE_NULL
    image_url_dict = {str(image.get('id')):image.get('url') for image in easy_store_product.get('images')}
    image_id_str = str(easy_store_variant_product.get('image_id'))

    variant_name = '-'+easy_store_variant_product.get('name') if easy_store_variant_product.get('name') else ''
    data = {
        'name':easy_store_product.get('name')+variant_name,
        'image': image_url_dict[image_id_str] if image_id_str in image_url_dict else product_image,
        'sku':easy_store_variant_product.get('sku'),
        'price':easy_store_variant_product.get('price'),
        'qty':easy_store_variant_product.get('inventory_quantity'),
        'tag':tags,
        'description':easy_store_product.get('description'),
        'user_subscription':user_subscription,
        'status':models.product.product.STATUS_ENABLED
    }
    
    return data


def to_lss_order(easy_store_order, lss_cart):

    order_data = {
        "campaign":lss_cart.campaign,
        "customer_id" : lss_cart.customer_id,
        "customer_name" : lss_cart.customer_name,
        "customer_img" : lss_cart.customer_img,
        "platform" : lss_cart.platform,
        "products":lss_cart.products,

        "payment_status" : models.order.order.PAYMENT_STATUS_PAID if easy_store_order.get('financial_status')=='paid' else models.order.order.PAYMENT_STATUS_AWAITING_PAYMENT,
        "status":models.order.order.STATUS_PROCEED,
        "discount" : float(easy_store_order.get('total_discount',0)),
        "subtotal" : float(easy_store_order.get('subtotal_price',0)),
        "shipping_cost" : float(easy_store_order.get('total_shipping',0)),
        "total" : float(easy_store_order.get('total_price',0)),
        "meta" : {'easy_store':easy_store_order},
    }

    return order_data
    # lss_order = models.order.order.Order.objects.create(**order_data)

    # lss_products = {}
    # order_products_data = []
    # for item in easy_store_order.get('line_items'):
    #     if item.get('variant_id') not in campaign_product_external_internal_map:
    #         continue
    #     campaign_product_data = campaign_product_external_internal_map[item.get('variant_id')]
        
    #     order_product_data={
    #         "name":campaign_product_data.get('name'),
    #         "price":float(item.get('price')),
    #         "image":campaign_product_data.get('image'),
    #         "qty":float(item.get('quantity')),
    #         "type":campaign_product_data.get('type'),
    #         "subtotal":float(item.get('price'))*float(item.get('quantity')),
    #         #relation:
    #         # "order_id":lss_order.id,
    #         "campaign_product_id":int(campaign_product_data.get('id'))
    #     }

    #     order_products_data.append(order_product_data)
    #     # database.lss.order_product.OrderProduct.create(**order_product_data)

    # return lss_order


        
        # lss_products[str(campaign_product_data.get('id'))] = {
        #     "order_product_id":None,   #TODO
        #     "name":campaign_product_data.get('name'),
        #     "image":campaign_product_data.get('image'),
        #     "price":float(item.get('price')),
        #     "type":campaign_product_data.get('type'),
        #     "qty":float(item.get('quantity')),
        #     "subtotal":float(item.get('subtotal'))
        # }


    




                            
                            
                           



    # return data

def to_lss_order_products(easy_store_order, lss_order, campaign_product_external_internal_map):
    order_products_data = []
    for item in easy_store_order.get('line_items'):
        if item.get('variant_id') not in campaign_product_external_internal_map:
            continue
        campaign_product_data = campaign_product_external_internal_map[item.get('variant_id')]
        
        order_product_data={
            "name":campaign_product_data.get('name'),
            "price":float(item.get('price')),
            "image":campaign_product_data.get('image'),
            "qty":float(item.get('quantity')),
            "type":campaign_product_data.get('type'),
            "subtotal":float(item.get('price'))*float(item.get('quantity')),
            #relation:
            "order_id":lss_order.id,
            "campaign_product_id":int(campaign_product_data.get('id'))
        }

        order_products_data.append(order_product_data)

    return order_products_data