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

        ordr_startr_order_data, = lib.util.getter.getdata(request,('order',),required=True)
        lss_pre_order_oid = ordr_startr_order_data.get('externalReferenceId')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(lss_pre_order_oid)
        campaign = pre_order.campaign
        if campaign.user_subscription.id != int(user_subscription_id):
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid')
        campaign_product_map = ordr_startr_lib.mapping_helper.get_campaign_product_map(campaign)

        lss_order_data = ordr_startr_lib.transformer.to_lss_order(ordr_startr_order_data, pre_order)

        models.order.order.Order.objects.create(**lss_order_data)

        ##update campaign product quantity:
        for product in ordr_startr_order_data.get('Items'):
            if product.get('_id') not in campaign_product_map:
                continue
            campaign_product_id = campaign_product_map[product.get('_id')]
            database.lss.campaign_product.CampaignProduct(id = campaign_product_id).sold(qty=product.get('qty'), sync=False)

        return Response('ok', status=status.HTTP_200_OK)


