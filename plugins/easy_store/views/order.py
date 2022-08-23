from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
import lib
import service


from automation import jobs

from pprint import pprint
PLUGIN_EASY_STORE = 'easy_store'
class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.order.order.Order.objects.none()

    @action(detail=False, methods=['POST'], url_path=r'webhook/create', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def easy_store_order_create_webhook(self, request):


        pprint(request.data)

        # {'order': 
            # {'id': 37069894, 
            # 'number': 1018, 
            # 'order_number': '#1018', 
            # 'remark': None, 
            # 'note': None, 
            # 'note_attributes': None, 
            # 'token': 'b9f68d89-f6fa-463d-85e2-870c7aaef113', 
            # 'cod_type': 0, 
            # 'cart_token': '5976c250-6472-42de-ab36-6a735526f060', 
            # 'total_line_items_price': '10.00', 
            # 'total_discount': '0.00', 
            # 'total_credit_used': '0.00', 
            # 'subtotal_price': '10.00', 
            # 'total_tax': '0.00', 
            # 'total_shipping': '1.00', 
            # 'total_price': '11.00', 
            # 'total_amount_include_transaction': '11.00', 
            # 'total_transaction_charge': 0.0, 
            # 'currency': 'MYR', 
            # 'currency_rate': '1.0', 
            # 'overpaid': None, 
            # 'amount_due': '11.00', 
            # 'total_refund_amount': '0.00', 
            # 'credit_used': '0.00', 
            # 'financial_status': 'unpaid', 
            # 'fulfillment_status': 'unfulfilled', 
            # 'taxes_included': False, 
            # 'browser_ip': '101.137.38.241', 
            # 'discount_codes': None, 
            # 'customer': {
                # 'id': 11748862, 
                # 'store_id': 1017218, 
                # 'user_id': None, 
                # 'pricelist_id': None, 
                # 'email': 'alphatw22193@gmail.com', 
                # 'first_name': 'Test', 
                # 'last_name': 'Test', 
                # 'phone': '12341234', 
                # 'birthdate': None, 
                # 'gender': None, 
                # 'country_code': 'TW', 
                # 'accepts_marketing': True, 
                # 'avatar_url': 'https://assets.imgix.net/~text?bg=1E6E00&txtclr=ffffff&w=200&h=200&txtsize=90&txt=TT&txtfont=Helvetica&txtalign=middle,center', 
                # 'locale': 'en_US', 
                # 'total_credit': '0.0', 
                # 'total_spent': '0.0', 
                # 'first_paid_order_id': None, 
                # 'last_order_id': None, 
                # 'last_order': None, 
                # 'last_order_at': None, 
                # 'total_order': 0, 
                # 'wholesale_enabled': False, 
                # 'source': 'sf', 
                # 'code': None, 
                # 'note': None, 
                # 'customer_code': None, 
                # 'is_verified': False, 
                # 'is_deleted': False, 
                # 'deleted_at': None, 
                # 'updated_at': '2022-08-23T16:18:22.000+08:00', 
                # 'created_at': '2022-08-23T16:18:22.000+08:00', 
                # 'deletion_job_id': None}, 
            # 'line_items': [{'id': 76324856, 'order_id': 37069894, 'product_id': 8041103, 'product_name': 'variant product', 'product_exist': 0, 'product_handle': 'variant-product', 'variant_id': 36344371, 'variant_name': 'ew', 'compare_at_price': '10.0', 'sku': 'asdf', 'barcode': 'asdf', 'price': '10.00', 'price_after_discount': '10.00', 'subtotal': '10.00', 'subtotal_after_discount': '10.00', 'total_discount': '0.00', 'discount_applies_once': 0, 'grams': '0.00', 'width': '0.00', 'height': '0.00', 'length': '0.00', 'quantity': 1, 'taxable': False, 'shipping_required': True, 'total_tax': '0.00', 'fulfilled_quantity': 0, 'fulfilled_quantity_sub': '0.00', 'unfulfill_quantity': 1, 'unfulfill_quantity_sub': '10.00', 'created_at': '2022-08-23T16:46:21.000+08:00', 'image': None, 'is_deleted': False}], 
            # 'billing_address': {'id': 17293552, 'order_id': 37069894, 'first_name': 'ttas', 'last_name': 'asdt', 'company': '', 'address1': 'asdf', 'address2': '', 'city': None, 'zip': '800', 'sub_district': None, 'sub_district_code': None, 'district': '\xe6\x96\xb0\xe8\x88\x88\xe5\x8d\x80', 'district_code': 'TW-KHH-800', 'province': '\xe9\xab\x98\xe9\x9b\x84\xe5\xb8\x82 Kaohsiung City', 'province_code': 'TW-KHH', 'country': 'Taiwan', 'country_code': 'TW', 'phone': '12341234', 'email': 'alphatw22193@gmail.com', 'latitude': None, 'longitude': None, 'is_deleted': False, 'deleted_at': None, 'updated_at': '2022-08-23T16:46:36.000+08:00', 'created_at': '2022-08-23T16:46:33.000+08:00'}, 'shipping_address': {'id': 15298958, 'order_id': 37069894, 'first_name': 'ttas', 'last_name': 'asdt', 'company': '', 'address1': 'asdf', 'address2': '', 'city': None, 'zip': '800', 'sub_district': None, 'sub_district_code': None, 'district': '\xe6\x96\xb0\xe8\x88\x88\xe5\x8d\x80', 'district_code': 'TW-KHH-800', 'province': '\xe9\xab\x98\xe9\x9b\x84\xe5\xb8\x82 Kaohsiung City', 'province_code': 'TW-KHH', 'country': 'Taiwan', 'country_code': 'TW', 'phone': '12341234', 'email': 'alphatw22193@gmail.com', 'latitude': None, 'longitude': None, 'preferred_start_at': None, 'preferred_end_at': None, 'is_deleted': False, 'deleted_at': None, 'updated_at': '2022-08-23T16:46:36.000+08:00', 'created_at': '2022-08-23T16:46:36.000+08:00'}, 'shipping_fees': {'id': 26695182, 'order_id': 37069894, 'name': 'test', 'handling_fee': '0.0', 'original_shipping_fee': 1.0, 'price': '1.00', 'total_discount': '0.00', 'discount_codes': None, 'shipping_id': 850300, 'created_at': '2022-08-23T16:46:36.000+08:00'}, 'pickup_location': None, 'transaction': [{'amount': '11.00', 'currency': 'MYR', 'gateway_type': 'bank-transfer', 'gateway_title': 'Bank transfer', 'gateway_method': 'bank-transfer', 'gateway_account': None, 'ref_number': '', 'created_at': '2022-08-23T16:46:38.000+08:00', 'status': 0, 'error_code': None, 'error_description': None, 'type': 'Transaction'}], 'source_name': 'sf', 'cancelled_at': None, 'processed_at': '2022-08-23T16:46:38.000+08:00', 'closed_at': None, 'created_at': '2022-08-23T16:46:38.000+08:00', 'updated_at': '2022-08-23T16:46:38.000+08:00', 'tax_lines': [{'title': 'SST', 'rate': '6.00', 'price': '0.00', 'shipping_tax': '0.00', 'shipping_taxable': False}]}}
        
        
        
        
        
        return Response('ok', status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'webhook/update', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def easy_store_order_update_webhook(self, request):


        print(request.data)

        return Response('ok', status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'webhook/cancel', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def easy_store_order_cancel_webhook(self, request):


        print(request.data)

        return Response('ok', status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'webhook/paid', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def easy_store_order_paid_webhook(self, request):


        print(request.data)

        return Response('ok', status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'webhook/partially_fulfilled', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def easy_store_order_partially_fulfilled_webhook(self, request):


        print(request.data)

        return Response('ok', status=status.HTTP_200_OK)


