from rest_framework import status, viewsets

from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib


from lib.authentication_class.v1_token_authentication import V1PermanentTokenAuthentication
from lib.permission_class.v1_token_permission import IsAuthenticated, IsAuthorizedByUserSubscription



PLUGIN_ORDR_STARTR = 'ordr_startr'

def ordr_startr_2_lss(ordr_startr_product, user_subscription):
    return {
        'name':ordr_startr_product.get('keyword'),
        'max_order_amount':ordr_startr_product.get('maxQty'),
        'sku':ordr_startr_product.get('SKU'),
        'order_code':ordr_startr_product.get('keyword'),
        'price':ordr_startr_product.get('price'),
        'qty':int(ordr_startr_product.get('stock'))-int(ordr_startr_product.get('sold')),
        'tag':[ordr_startr_product.get('supplierName')],
        'description':ordr_startr_product.get('description'),
        'user_subscription':user_subscription
    }


def update_category(ordr_startr_product, product_categories, tag_set):
    tag_name = ordr_startr_product.get('supplierName')
    if tag_name not in tag_set:
            product_categories.append(tag_name)
            tag_set.add(tag_name)
        
class ProductViewSet(viewsets.GenericViewSet):
    queryset = models.product.product.Product.objects.all()

    @action(detail=False, methods=['PUT'], url_path=r'sync/(?P<user_subscription_id>[^/.]+)', permission_classes=(IsAuthenticated,IsAuthorizedByUserSubscription), authentication_classes=[V1PermanentTokenAuthentication,])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def export_product_from_ordr_startr(self, request, user_subscription_id):

        user_subscription = models.user.user_subscription.UserSubscription.objects.get(id=user_subscription_id)

        added_products, updated_products, deleted_products = lib.util.getter.getdata(request, ('Added','Updated','Deleted'),required=False)

        product_categories:list = user_subscription.meta.get('product_categories',[])
        tag_set:set = set(product_categories) 

        product_dict = {product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id') : product.id for product in user_subscription.products.all() if product.meta.get(PLUGIN_ORDR_STARTR,{}).get('id')}
        
        for product in added_products:
            if product.get('_id') in product_dict:
                continue
            data = ordr_startr_2_lss(product, user_subscription)
            lss_product = models.product.product.Product.objects.create(**data, meta={PLUGIN_ORDR_STARTR:{'id':product.get('_id')}})
            product_dict[product.get('_id')] = lss_product.id
            update_category(product, product_categories, tag_set)
            
        for product in updated_products:
            
            if product.get('_id') not in product_dict:
                continue
            data = ordr_startr_2_lss(product, user_subscription)
            models.product.product.Product.objects.filter(id=product_dict[product.get('_id')]).update(**data)
            update_category(product, product_categories, tag_set)

        for product in deleted_products:
            if product.get('_id') not in product_dict:
                continue
            models.product.product.Product.objects.filter(id=product_dict[product.get('_id')]).update(status=models.product.product.STATUS_DISABLED)

        user_subscription.save()

        return Response('ok', status=status.HTTP_200_OK)
