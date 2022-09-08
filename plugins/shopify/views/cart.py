from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib
import service

from .. import service as shopify_service
from .. import lib as shopify_lib

from automation import jobs

PLUGIN_SHOPIFY = 'shopify'

class CartViewSet(viewsets.GenericViewSet):
    queryset = models.order.pre_order.PreOrder.objects.none()

    @action(detail=False, methods=['GET'], url_path=r'gateway/(?P<cart_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_shopify_checkout_gateway(self, request, cart_oid):
        recaptcha_token, = lib.util.getter.getparams(request, ('recaptcha_token',), with_user=False)
        
        code, response = service.recaptcha.recaptcha.verify_token(recaptcha_token)
        print(response)
        if code!=200 or not response.get('success'):
            raise lib.error_handle.error.api_error.ApiVerifyError('Please Refresh The Page And Retry Again')

        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(cart_oid)    #temp
        campaign = pre_order.campaign
        user_subscription = campaign.user_subscription

        credential = user_subscription.user_plan.get('plugins',{}).get('shopify',{})

        if not credential:
            raise lib.error_handle.error.api_error.ApiVerifyError('no_plugin')
        
        internal_external_map = shopify_lib.mapping_helper.CampaignProduct.get_internal_external_map(campaign)

        line_items = []
        for campaign_product_id_str, product in pre_order.products.items():
            if campaign_product_id_str not in internal_external_map:
                continue
            variant_id = internal_external_map[campaign_product_id_str]
            line_items.append({'variant_id': variant_id, 'quantity': product.get('qty')})
        
        print (line_items)

        return Response('checkout_url', status=status.HTTP_200_OK)