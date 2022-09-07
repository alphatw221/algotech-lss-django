from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib
import service

from .. import service as easy_store_service
from .. import lib as easy_store_lib

from automation import jobs

PLUGIN_EASY_STORE = 'easy_store'

class CartViewSet(viewsets.GenericViewSet):
    queryset = models.order.pre_order.PreOrder.objects.none()

    @action(detail=False, methods=['GET'], url_path=r'gateway/(?P<cart_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_easy_store_checkout_gateway(self, request, cart_oid):

        recaptcha_token, = lib.util.getter.getparams(request, ('recaptcha_token',), with_user=False)
        
        code, response = service.recaptcha.recaptcha.verify_token(recaptcha_token)

        if code!=200 or not response.get('success'):
            raise lib.error_handle.error.api_error.ApiVerifyError('Please Refresh The Page And Retry Again')

        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(cart_oid)    #temp
        campaign = pre_order.campaign
        user_subscription = campaign.user_subscription

        credential = user_subscription.user_plan.get('plugins',{}).get('easy_store',{})

        if not credential:
            raise lib.error_handle.error.api_error.ApiVerifyError('no_plugin')

        internal_external_map = easy_store_lib.mapping_helper.CampaignProduct.get_internal_external_map(campaign)

        line_items = []
        for campaign_product_id_str,product in pre_order.products.items():
          if campaign_product_id_str not in internal_external_map:
              continue
          variant_id = internal_external_map[campaign_product_id_str]
          line_items.append({'variant_id':variant_id, 'quantity':product.get('qty')})
        
        success, data = easy_store_service.checkouts.create_checkout(credential.get('shop'), credential.get('access_token'), line_items)
        if not success:
            raise lib.error_handle.error.api_error.ApiCallerError('please place your order again')
        
        checkout = data.get('checkout')
        id = checkout.get('id')
        token = checkout.get('token')
        cart_token = checkout.get('cart_token')
        checkout_url = checkout.get('checkout_url')
        
        meta_data = {'easy_store':{
                            "id":id,
                            "token":token,
                            "cart_token":cart_token,
                            "checkout_url":checkout_url,
                        }}
        campaign.meta[cart_token]=pre_order.id
        campaign.save()
        pre_order.meta.update(meta_data)
        pre_order.save()

        return Response(checkout_url, status=status.HTTP_200_OK)
