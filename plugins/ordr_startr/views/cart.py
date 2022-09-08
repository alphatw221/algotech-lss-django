from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib
import service

from .. import service as ordr_startr_service
from .. import lib as ordr_startr_lib

from automation import jobs

PLUGIN_ORDR_STARTR = 'ordr_startr'

class CartViewSet(viewsets.GenericViewSet):
    queryset = models.order.pre_order.PreOrder.objects.none()

    @action(detail=False, methods=['GET'], url_path=r'gateway/(?P<cart_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_ordr_startr_checkout_gateway(self, request, cart_oid):

        recaptcha_token, = lib.util.getter.getparams(request, ('recaptcha_token',), with_user=False)
        
        code, response = service.recaptcha.recaptcha.verify_token(recaptcha_token)

        if code!=200 or not response.get('success'):
            raise lib.error_handle.error.api_error.ApiVerifyError('Please Refresh The Page And Retry Again')

        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(cart_oid)    #temp
        campaign = pre_order.campaign
        user_subscription = campaign.user_subscription

        credential = user_subscription.user_plan.get('plugins',{}).get(PLUGIN_ORDR_STARTR,{})

        if not credential:
            raise lib.error_handle.error.api_error.ApiVerifyError('no_plugin')
        internal_external_map = ordr_startr_lib.mapping_helper.CampaignProduct.get_internal_external_map(campaign)

        product_items = []
        for campaign_product_id_str,product in pre_order.products.items():
          if campaign_product_id_str not in internal_external_map:
              continue
          campaign_product_data = internal_external_map[campaign_product_id_str]
          product_items.append({'Id':campaign_product_data.get('id'), 'Keyword':campaign_product_data.get('order_code'), 'Qty':product.get('qty')})
        
        success, data = ordr_startr_service.order.create_order(key=credential.get('key'), cart_oid=cart_oid, user_id=pre_order.customer_id, user_name=pre_order.customer_name, platform=pre_order.platform, product_items=product_items)
        
        

        # print(data)
        # if not success:
        #     raise lib.error_handle.error.api_error.ApiCallerError('please place your order again')

        # print(data)
        
        # checkout = data.get('checkout')
        # id = checkout.get('id')
        # token = checkout.get('token')
        # cart_token = checkout.get('cart_token')
        # checkout_url = checkout.get('checkout_url')
        
        # meta_data = {'easy_store':{
        #                     "id":id,
        #                     "token":token,
        #                     "cart_token":cart_token,
        #                     "checkout_url":checkout_url,
        #                 }}
        # campaign.meta[cart_token]=pre_order.id
        # campaign.save()
        # pre_order.meta.update(meta_data)
        # pre_order.save()
        # print(checkout_url)
        #https://localhost:3000/buyer/recaptcha/ordr_startr/6315979a19ec784a705c4697

        return Response(data.get('CheckoutUrl'), status=status.HTTP_200_OK)
