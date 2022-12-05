import os
import config
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception as e:
    pass


from plugins.ordr_startr import service as ordr_startr_service
from plugins.ordr_startr import lib as ordr_startr_lib
from api import models

import traceback
PLUGIN_ORDR_STARTR = 'ordr_startr'

def export_product_job(user_subscription_id, credential):
    try:
        


        user_subscription = models.user.user_subscription.UserSubscription.objects.get(id=user_subscription_id)

        models.product.product.Product.objects.filter(user_subscription=user_subscription).delete()
        user_subscription.meta['product_categories']=[]

        product_categories:list = user_subscription.meta.get('product_categories',[])

        product_dict = {product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id') : product.id for product in user_subscription.products.all() if product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id')}
        tag_set:set = set(product_categories) 
        

        success, products = ordr_startr_service.product.get_products(credential.get('key'))

        if not success:
            raise Exception()
        

        for product in products:
            lss_product_data = ordr_startr_lib.transformer.to_lss_product(product,user_subscription)
            ordr_startr_lib.category_helper.update_category(product,product_categories,tag_set)
            if product.get('_id') in product_dict:
                lss_product_id = product_dict[product.get('_id')]
                models.product.product.Product.objects.filter(id=lss_product_id).update(**lss_product_data)
            else:
                meta_data = {PLUGIN_ORDR_STARTR:{'id':product.get('_id')}}
                lss_product = models.product.product.Product.objects.create(**lss_product_data, meta=meta_data)
                product_dict[product.get('_id')] = lss_product.id

        user_subscription.save()


        ordr_startr_service.channels.export_product.send_result_data(user_subscription.id,{'result':'complete'})
    except Exception:
        print(traceback.format_exc())
        ordr_startr_service.channels.export_product.send_result_data(user_subscription.id,{'result':'fail'})

