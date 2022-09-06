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




