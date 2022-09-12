from rest_framework import status, viewsets

from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib


from lib.authentication_class.v1_token_authentication import V1PermanentTokenAuthentication
from lib.permission_class.v1_token_permission import IsAuthenticated, IsAuthorizedByUserSubscription

from .. import lib as ordr_startr_lib
import database
PLUGIN_ORDR_STARTR = 'ordr_startr'
from bson.objectid import ObjectId

class OrderViewSet(viewsets.GenericViewSet):
    queryset = models.order.order.Order.objects.none()

    @action(detail=False, methods=['PUT'], url_path=r'callback/(?P<user_subscription_id>[^/.]+)/payment/complete', permission_classes=(IsAuthenticated,IsAuthorizedByUserSubscription), authentication_classes=[V1PermanentTokenAuthentication,])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def order_payment_complete_callback(self, request, user_subscription_id):

        ordr_startr_order_data, ordr_startr_products_data = lib.util.getter.getdata(request,('order', 'products'),required=True)
        lss_pre_order_oid = ordr_startr_order_data.get('ExternalReferenceId')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(lss_pre_order_oid)
        campaign = pre_order.campaign
        if campaign.user_subscription.id != int(user_subscription_id):
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid')
        campaign_product_external_internal_map = ordr_startr_lib.mapping_helper.CampaignProduct.get_external_internal_map(campaign)


        lss_order_data = ordr_startr_lib.transformer.to_lss_order(ordr_startr_order_data, pre_order, campaign_product_external_internal_map)

        lss_order = models.order.order.Order.objects.create(**lss_order_data)

        for campaign_product_id_str,product in pre_order.products.items():
            database.lss.campaign_product.CampaignProduct(id = int(campaign_product_id_str)).customer_return(product.get('qty'), sync=False) #do this anyway
        database.lss.pre_order.PreOrder(id=pre_order.id).reset_pre_order(sync=False)            #do this anyway
        database.lss.order_product.OrderProduct.transfer_to_order(pre_order, lss_order)         #do this anyway

        ##update campaign product quantity:
        for product in ordr_startr_products_data:
            if product.get('_id') not in campaign_product_external_internal_map:
                continue
            lss_campaign_product_data = campaign_product_external_internal_map[product.get('_id')]
            database.lss.campaign_product.CampaignProduct(id = lss_campaign_product_data.get('id')).sold_from_external(qty=product.get('sold'), sync=False)

        return Response('ok', status=status.HTTP_200_OK)


