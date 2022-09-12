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
            if tags:
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

  
