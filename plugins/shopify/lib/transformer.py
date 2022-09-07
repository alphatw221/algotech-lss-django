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

