from api import models

def to_lss_product(ordr_startr_product, user_subscription):
    return {
        'name':ordr_startr_product.get('keyword'),
        'max_order_amount':ordr_startr_product.get('maxQty'),
        'sku':ordr_startr_product.get('SKU'),
        'order_code':ordr_startr_product.get('keyword'),
        'price':ordr_startr_product.get('price'),
        'qty':int(ordr_startr_product.get('stock'))-int(ordr_startr_product.get('sold')),
        'tag':[ordr_startr_product.get('supplierName')],
        'description':ordr_startr_product.get('description'),
        'user_subscription':user_subscription,
        'status':models.product.product.STATUS_DISABLED if ordr_startr_product.get('visible')==False else models.product.product.STATUS_ENABLED
        

    }

