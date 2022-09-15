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

# from automation import jobs
# from requests import request as request_url

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

        line_items = []
        for campaign_product_id_str, product in pre_order.products.items():
            if campaign_product_id_str not in internal_external_map:
                continue
            variant_id = internal_external_map[campaign_product_id_str]
            line_items.append({'variant_id': variant_id, 'quantity': product.get('qty')})
        
        success, response = shopify_service.checkouts.create_checkout(credential.get('shop'), credential.get('access_token'), line_items, pre_order.discount)
        if not success:
            raise lib.error_handle.error.api_error.ApiCallerError('please try again')

        invoice_url = response.get('draft_order',{}).get('invoice_url')
        order_key = invoice_url[-32:]
        campaign.meta[order_key] = pre_order.id
        campaign.save()

        return Response(invoice_url, status=status.HTTP_200_OK)



        # {
        #     'draft_order': {
        #         'id': 929987330239, 
        #         'note': None, 
        #         'email': None, 
        #         'taxes_included': False, 
        #         'currency': 'TWD', 
        #         'invoice_sent_at': None, 
        #         'created_at': '2022-09-14T00:36:13+08:00', 
        #         'updated_at': '2022-09-14T00:36:13+08:00', 
        #         'tax_exempt': False, 
        #         'completed_at': None, 
        #         'name': '#D22', 
        #         'status': 'open', 
        #         'line_items': [{'id': 57449776382143, 'variant_id': 41918730272959, 'product_id': 7340180799679, 'title': 'frog w.', 'variant_title': None, 'sku': '', 'vendor': 'frog sweat home', 'quantity': 1, 'requires_shipping': True, 'taxable': True, 'gift_card': False, 'fulfillment_service': 'manual', 'grams': 0, 'tax_lines': [{'rate': 0.05, 'title': 'VAT', 'price': '0.50'}], 
        #             'applied_discount': None, 
        #             'name': 'frog w.', 
        #             'properties': [], 
        #             'custom': False, 
        #             'price': '10.00', 
        #             'admin_graphql_api_id': 'gid://shopify/DraftOrderLineItem/57449776382143'}], 
        #         'shipping_address': None, 
        #         'billing_address': None, 
        #         'invoice_url': 'https://frog-sweat-home.myshopify.com/62622073023/invoices/f1709525213b97862284beae33ac6bcf', 
        #         'applied_discount': None, 
        #         'order_id': None, 
        #         'shipping_line': None, 
        #         'tax_lines': [{'rate': 0.05, 'title': 'VAT', 'price': '0.50'}], 
        #         'tags': '', 
        #         'note_attributes': [],
        #         'total_price': '10.50', 
        #         'subtotal_price': '10.00', 
        #         'total_tax': '0.50', 
        #         'payment_terms': None, 
        #         'admin_graphql_api_id': 'gid://shopify/DraftOrder/929987330239', 
        #         'customer': None}}