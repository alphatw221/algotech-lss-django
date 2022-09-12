import json
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
from requests import request as request_url

PLUGIN_SHOPIFY = 'shopify'

class CartViewSet(viewsets.GenericViewSet):
    queryset = models.order.pre_order.PreOrder.objects.none()

    @action(detail=False, methods=['GET'], url_path=r'gateway/(?P<cart_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_shopify_checkout_gateway(self, request, cart_oid):
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(cart_oid)    #temp
        campaign = pre_order.campaign
        user_subscription = campaign.user_subscription

        credential = user_subscription.user_plan.get('plugins',{}).get('shopify',{})

        if not credential:
            raise lib.error_handle.error.api_error.ApiVerifyError('no_plugin')
        
        internal_external_map = shopify_lib.mapping_helper.CampaignProduct.get_internal_external_map(campaign)

        draft_order = {}
        line_items = []
        for campaign_product_id_str, product in pre_order.products.items():
            if campaign_product_id_str not in internal_external_map:
                continue
            variant_id = internal_external_map[campaign_product_id_str]
            line_items.append({'variant_id': variant_id, 'quantity': product.get('qty')})
        
        draft_order['line_items'] = line_items
        
        if pre_order.discount > 0:
            applied_discount = {
                "description": "Referr discount",
                "value_type": "fixed_amount",
                "value": str(pre_order.discount),
                "amount": str(pre_order.discount),
                "title": "Referr discount"
            }
            draft_order['applied_discount'] = applied_discount
        
        data = { "draft_order": draft_order }
        response = request_url("POST", f"https://{credential.get('shop')}/admin/api/2022-07/draft_orders.json", headers={'X-Shopify-Access-Token': credential.get('access_token')}, json=data, timeout=5)

        if not response.status_code != '201':
            raise 'failed'
        
        checkout_url = json.loads(response.text).get('draft_order').get('invoice_url')
        order_key = checkout_url[checkout_url.find('com/') + 4 : checkout_url.find('/invoices')]        

        campaign.meta[order_key] = pre_order.id
        campaign.save()

        return Response(checkout_url, status=status.HTTP_200_OK)