from ast import operator
import functools
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from api.models.order.order import Order, OrderSerializer, OrderSerializerUpdatePaymentShipping
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError, platform_dict
from api.utils.common.common import getparams
from api.utils.common.order_helper import OrderHelper

from mail.sender.sender import *
from django.http import HttpResponse
from backend.pymongo.mongodb import db
import xlsxwriter, os.path, io, datetime
from io import StringIO
from django.conf import settings
from dateutil import parser
import functools
 
import operator
from django.db.models import Q

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
def get_title_map():
    title_map = {
            'id': 'Id',
            'created_at': 'Order Date',
            'customer_name': 'Customer Name',
            'platform': 'Platform',
            'shipping_email': 'E-mail',
            'shipping_phone': 'Phone',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'total': 'Total',
            'payment_method': 'Payment Method',
            'shipping_first_name': 'Shipping First Name',
            'shipping_last_name': 'Shipping Last Name',
            'shipping_phone': 'Shipping Phone',
            'shipping_postcode': 'Postcode',
            'shipping_region': 'Region',
            'shipping_location': 'Location',
            'shipping_address_1': 'Shipping Address 1',
            'shipping_method': 'Shipping Method',
            'pick_up_date': 'Pick Up Date',
            'pick_up_store': 'Pick Up Store',
            'shipping_remark': 'Remark',
            'status': 'Payment Status',
            'last_five_digit': 'Payment Record',
            'payment_card_type': 'Payment Card Type',
            'payment_card_number': 'Payment Card Number'
        }
    return title_map


def verify_seller_request(api_user, platform_name, platform_id, campaign_id, order_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign_from_platform(platform, campaign_id)

    if order_id:
        if not Order.objects.get(id=order_id):
            raise ApiVerifyError('no order found')
        order = Order.objects.get(id=order_id)
        return platform, campaign, order

    return platform, campaign

class OrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class OrderViewSet(viewsets.ModelViewSet):
    
    queryset = Order.objects.all().order_by('id')
    serializer_class = OrderSerializer
    filterset_fields = []
    
    @action(detail=True, methods=['GET'], url_path=r'seller_retrieve', permission_classes = (IsAuthenticated,))
    @api_error_handler
    def seller_retrieve_order(self, request, pk=None):

        api_user, platform_id, platform_name = getparams(
            request, ("platform_id", "platform_name"),with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        order=Verify.get_order(pk)
        Verify.get_campaign_from_platform(platform, order.campaign.id)

        # _, _, order = verify_seller_request(
        #     api_user, platform_name, platform_id, campaign_id, order_id=pk)

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'seller_list', permission_classes = (IsAuthenticated,))
    @api_error_handler
    def seller_list_order(self, request):
        api_user, platform_id, platform_name, campaign_id, order_by = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "order_by"))

        _, campaign = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id)

        queryset = campaign.orders.all()
        # TODO filtering
        if order_by:
            queryset = queryset.order_by(order_by)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            result = self.get_paginated_response(
                serializer.data)
            data = result.data
        else:
            serializer = OrderSerializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'seller_cancel', permission_classes = (IsAuthenticated,))
    @api_error_handler
    def seller_cancel_order(self, request, pk=None):

        api_user, platform_id, platform_name = getparams(
            request, ("platform_id", "platform_name"),with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        order=Verify.get_order(pk)
        Verify.get_campaign_from_platform(platform, order.campaign.id)
        
        pre_order = OrderHelper.cancel(api_user, order)

        return Response('order canceled', status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'seller_delete', permission_classes = (IsAuthenticated,))
    @api_error_handler
    def seller_delete_order(self, request, pk=None):

        api_user, platform_id, platform_name = getparams(
            request, ("platform_id", "platform_name"),with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        order=Verify.get_order(pk)
        Verify.get_campaign_from_platform(platform, order.campaign.id)
        
        order = OrderHelper.delete(api_user, order)
        
        return Response('order deleted', status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'report', permission_classes = (IsAuthenticated,))
    @api_error_handler
    def seller_order_report(self, request):
        api_user, platform_id, platform_name, campaign_id, column_list = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "column_list"), with_user=True, seller=True)
        
        platform, campaign = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id)
        
        #check_download_at:
        # last_report_download_at = campaign.meta.get('last_report_download_at',None)
        # if last_report_download_at and datetime.datetime.timestamp(last_report_download_at)+settings.ORDER_REPORT_DOWNLOAD_INTERVAL > datetime.datetime.timestamp(datetime.datetime.now()):
        #     raise ApiVerifyError('frequently download')
        # campaign.meta['last_report_download_at']=datetime.datetime.now() 
        # campaign.save()

        column_list = column_list.split(',')
        title_map = get_title_map()
        campaign_title = db.api_campaign.find_one({'id': int(campaign_id)})['title']
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=' + campaign_title + '.xlsx'
 
        workbook = xlsxwriter.Workbook(response, {'in_memory': True})
        worksheet = workbook.add_worksheet()
        header = workbook.add_format({
            'bold': True,
            'bg_color': '#F7F7F7',
            'color': 'black',
            'align': 'center',
            'valign': 'top',
            'border': 1
        })
        int_center = workbook.add_format({
            'align': 'center'
        })
        title_form = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': 18,
            'border': 1
        })
        info_form = workbook.add_format({
            'align': 'center',
            'bold': True,
            'font_size': 13,
            'border': 1
        })
        
        products_count = 0
        campaign_products = db.api_campaign_product.find({'campaign_id': int(campaign_id)})
        for campaign_product in campaign_products:
            products_count += 1
        worksheet.merge_range(0, 0, 0, len(column_list) + products_count - 1, campaign_title + ' Order Report', title_form)
        worksheet.merge_range(1, 0, 1, 5, 'Contact Info', info_form)
        worksheet.merge_range(1, 6, 1, 13, 'Delivery Info', info_form)
        worksheet.merge_range(1, 14, 1, 19, 'Payment Info', info_form)
        worksheet.merge_range(1, 20, 1, 20 + products_count - 1, 'Order Info', info_form)

        row, column = 2, 0
        for column_title in column_list:
            worksheet.write(row, column, title_map[column_title], header)
            if len(column_title) >= 8:
                    worksheet.set_column(column, column, len(title_map[column_title]) + 2)
            column += 1
        
        product_column_dict = {}
        campaign_products = db.api_campaign_product.find({'campaign_id': int(campaign_id)})
        for campaign_product in campaign_products:
            worksheet.write(row, column, campaign_product['name'], header)
            product_column_dict[str(campaign_product['id'])] = column
            column += 1
        row += 1
        column = 0

        order_id_list = []
        order_ids = db.api_order.find({'campaign_id': int(campaign_id)})
        for order_id in order_ids:
            order_id_list.append(order_id['id'])
        
        total_count = 0
        num_col_total = 0
        # for each order data 1 by 1
        for order_id in order_id_list:
            order_data = db.api_order.find_one({'id': order_id})

            for column_title in column_list:
                if column_title in ['pick_up_date', 'pick_up_store', 'last_five_digit']:
                    col_data = ''
                    try:
                        col_data = order_data['meta'][column_title]
                    except:
                        col_data = ''
                    worksheet.write(row, column, col_data)
                elif column_title == 'created_at':
                    col_data = order_data[column_title].strftime("%Y-%m-%d")
                    worksheet.write(row, column, col_data)
                elif column_title in ['payment_card_type', 'payment_card_number']:
                    worksheet.write(row, column, '')
                else:
                    col_data = order_data[column_title]
                    if column_title == 'total':
                        total_count += col_data
                        num_col_total = column
                    if type(col_data) == int or type(col_data) == float:
                        worksheet.write(row, column, col_data, int_center)
                    else:
                        worksheet.write(row, column, col_data)
                column += 1
            
            products = order_data['products']
            for campaing_product_id_str, product in products.items():
                worksheet.write(row, product_column_dict[campaing_product_id_str], product['qty'])
                
            row += 1
            column = 0
        worksheet.write(row , num_col_total, total_count, int_center)
        workbook.close()
        
        return response

# --------------------- buyer --------------------------------------------

    from rest_framework.permissions import BasePermission

    class IsOrderCustomer(BasePermission):

        def has_permission(self, request, view):
            try:
                pk = view.kwargs.get('pk')
                api_user = Verify.get_customer_user(request)
                order = Verify.get_order(pk)
                Verify.user_match_order(api_user, order)
            except Exception:
                return False
            return True
            
    @action(detail=True, methods=['GET'], url_path=r'buyer_retrieve')
    @api_error_handler
    def buyer_retrieve_order(self, request, pk=None):

        # OPERATION_CODE_NAME: AGILE
        # if request.user.id in settings.ADMIN_LIST:
        #     order = Order.objects.get(id=pk)
        #     serializer = OrderSerializer(order)

        #     return Response(serializer.data, status=status.HTTP_200_OK)


        # 先檢查exists 才給request get
        # api_user, = getparams(
        #     request, (), seller=False)
        api_user=None
        order = Order.objects.get(id = pk)
        Verify.user_match_pre_order(api_user, order)

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'buyer_submit')
    @api_error_handler
    def update_buyer_submit(self, request, pk=None):
        # api_user, platform_name, campaign_id = getparams(
        #     request, ("platform_name", "campaign_id"), seller=False)

        # order = verify_buyer_request(
        #     api_user, platform_name, campaign_id)
        platform_name, campaign_id = getparams(
            request, ("platform_name", "campaign_id"), with_user=False, seller=False)
        
        # request.data['status'] = 'complete'
        # serializer = OrderSerializerUpdatePaymentShipping(order, data=request.data, partial=True)
        # if not serializer.is_valid():
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # serializer.save()

        db.api_order.update_one({'id': int(pk)}, {'$set': {'status': 'complete'}})

        # order = verify_buyer_request(
        #     api_user, platform_name, campaign_id, check_info=True)
        order = Order.objects.get(id = pk)
        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path=r'buyer_cancel')
    @api_error_handler
    def update_buyer_cancel(self, request, pk=None):
        # api_user, = getparams(
        #     request, (), seller=False)
        api_user = None
        order = Order.objects.get(id = pk)
        Verify.user_match_pre_order(api_user, order)

        # api_user, platform_name, campaign_id = getparams(
        #     request, ("platform_name", "campaign_id"), seller=False)
        
        # order = verify_buyer_request(
        #     api_user, platform_name, campaign_id)
        if order.status != 'unpaid':
            pre_order = OrderHelper.cancel(api_user, order)

            return Response('order canceled', status=status.HTTP_200_OK)
        else:
            return Response('order submited, can not cancel by customer', status=status.HTTP_400_BAD_REQUEST)

    
    @action(detail=False, methods=['GET'], url_path=r'buyer_list', permission_classes = (IsAuthenticated,))
    @api_error_handler
    def list_buyer_history_order(self, request):

        api_user, = getparams(
            request, (), with_user=True, seller=False)

        query_list=[]

        if api_user.facebook_info.get("id"):
            query_list.append( Q(customer_id = api_user.facebook_info.get("id")) )

        for channel_id, _ in api_user.youtube_info:
            query_list.append( Q(customer_id = channel_id) )

        if api_user.instagram_info.get("id"):
            query_list.append( Q(customer_id = api_user.instagram_info.get("id")) )
            
        orders = Order.objects.filter(functools.reduce(operator.or_, query_list))
 
        return Response(OrderSerializer(orders, many=True).data, status=status.HTTP_200_OK)