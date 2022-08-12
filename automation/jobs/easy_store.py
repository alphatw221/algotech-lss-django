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
        sku_dict = { product.sku:product.id  for product in user_subscription.products.all() if product.sku}

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
                tags = [collection.get('name') for collection in  product.get('collections') if collection.get('name')]
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
                        lss_product.tags = tags
                        lss_product.qty = qty
                        lss_product.status = models.product.product.STATUS_ENABLED
                        lss_product.meta.update(meta_data)
                        lss_product.save()
                    else:
                        models.product.product.Product.objects.create(
                            user_subscription = user_subscription, name = name, price=price, sku=sku, tags=tags, qty = qty, status = models.product.product.STATUS_ENABLED, meta=meta_data)

            page+=1


    except Exception:
        print(traceback.format_exc())
        # easy_store_service.channels.export_product.send_result_data(user_subscription_id,{'result':'fail'})