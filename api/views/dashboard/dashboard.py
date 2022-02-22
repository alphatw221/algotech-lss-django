from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from api.models.order.order import Order, OrderSerializer
from api.models.order.pre_order import PreOrder, PreOrderSerializer
from api.utils.common.verify import Verify
from api.utils.common.common import *

from backend.pymongo.mongodb import db
from dateutil.relativedelta import relativedelta
import datetime, operator

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.common.common import getparams
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from django.core.paginator import Paginator
from django.shortcuts import render

# class PreOrderPagination(PageNumberPagination):
#     page_query_param = 'page'
#     page_size_query_param = 'page_size'

# class OrderPagination(PageNumberPagination):
#     page_query_param = 'page'
#     page_size_query_param = 'page_size'


def verify_seller_request(api_user):
    Verify.verify_user(api_user)
    return True

def get_camaign_list(user_id):
    campaign_id_list = []
    campaigns = db.api_campaign.find({'created_by_id': user_id})
    for campaign in campaigns:
        campaign_id_list.append(campaign['id'])
    return campaign_id_list


class DashboardViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all().order_by('id')
    serializer_class = OrderSerializer
    filterset_fields = []

    @action(detail=False, methods=['GET'], url_path=r'total_sales')
    @api_error_handler
    def total_sales(self, request):
        api_user = request.user.api_users.get(type='user')
        is_user = verify_seller_request(api_user)
        total_sales = 0

        if is_user:
            user_id = api_user.id
            print (user_id)
            campaign_id_list = get_camaign_list(user_id)
            
            order_datas = db.api_order.find({'campaign_id': {'$in': campaign_id_list}})
            for order_data in order_datas:
                products = order_data['products']
                for key, val in products.items():
                    total_sales += val['qty']
        salesJson = { 'total_sales': total_sales } 

        return Response(salesJson, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'total_revenue')
    @api_error_handler
    def seller_total_revenue(self, request):
        api_user = request.user.api_users.get(type='user')
        is_user = verify_seller_request(api_user)
        total_revenue = 0

        if is_user:
            user_id = api_user.id
            campaign_id_list = get_camaign_list(user_id)

            order_datas = db.api_order.find({'campaign_id': {'$in': campaign_id_list}})
            for order_data in order_datas:
                total_revenue += order_data['total']
        revenueJson = { 'total_revenue': total_revenue }
        
        return Response(revenueJson, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'total_pending')
    @api_error_handler
    def seller_total_pending(self, request):
        api_user = request.user.api_users.get(type='user')
        is_user = verify_seller_request(api_user)
        total_pending = 0

        if is_user:
            user_id = api_user.id
            campaign_id_list = get_camaign_list(user_id)
            pre_order_total = 0
            order_total = 0

            pre_orders = db.api_pre_order.find({'campaign_id': {'$in': campaign_id_list}})
            for pre_order in pre_orders:
                products = pre_order['products']    
                for key, val in products.items():
                    pre_order_total += val['qty']
                
            order_datas = db.api_order.find({'campaign_id': {'$in': campaign_id_list}})
            for order_data in order_datas:
                products = order_data['products']
                for key, val in products.items():
                    order_total += val['qty'] 
            try:
                total_pending = 1 - order_total / (pre_order_total + order_total)
            except:
                total_pending = 0
        pendingJson = { 'total_pending': '{:.2%}'.format(total_pending) }
    
        return Response(pendingJson, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'sales_by_month')
    @api_error_handler
    def seller_sales_by_month(self, request):
        api_user = request.user.api_users.get(type='user')
        is_user = verify_seller_request(api_user)
        pending_by_month = {}

        if is_user:
            user_id = api_user.id
            campaign_id_list = get_camaign_list(user_id)

            nowdate = datetime.datetime.now()
            startDate = datetime.datetime(nowdate.year, nowdate.month, 1) + relativedelta(months=1)
            endDate = datetime.datetime(2021, 10, 1)
            while (startDate >= endDate):
                thisEndDate = startDate + relativedelta(months=-1)
                date = str(thisEndDate.year) + '-' + str(thisEndDate.month)
                order_total = 0
                pre_order_total = 0
                
                pre_orders = db.api_pre_order.find({'campaign_id': {'$in': campaign_id_list}, 'created_at': {'$gte': thisEndDate, '$lt': startDate}})
                for pre_order in pre_orders:
                    products = pre_order['products']    
                    for key, val in products.items():
                        pre_order_total += val['qty']

                order_datas = db.api_order.find({'campaign_id': {'$in': campaign_id_list}, 'created_at': {'$gte': thisEndDate, '$lt': startDate}})
                for order_data in order_datas:
                    products = order_data['products']
                    for key, val in products.items():
                        order_total += val['qty'] 
                
                if pre_order_total + order_total == 0:
                    pending_by_month[date] = '0.00%'
                else:
                    total_pending = 1 - order_total / (pre_order_total + order_total)
                    pending_by_month[date] = '{:.2%}'.format(total_pending)

                startDate = startDate + relativedelta(months=-1)
            
        return Response(pending_by_month, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'top_campaign')
    @api_error_handler
    def seller_top_campaign(self, request):
        api_user = request.user.api_users.get(type='user')
        sort = request.query_params.get('sort')
        is_user = verify_seller_request(api_user)   
        campaignRank = {}

        if is_user:
            user_id = api_user.id
            campaign_id_list = get_camaign_list(user_id)

            if sort == 'comment':
                for campaign_id in campaign_id_list:
                    campaign_count = db.api_campaign_comment.count({'campaign_id': campaign_id})
                    campaignRank[db.api_campaign.find_one({'id': campaign_id})['title']] = campaign_count
                campaignRank = dict(sorted(campaignRank.items(), key=operator.itemgetter(1), reverse=True))

            elif sort == 'order': 
                for campaign_id in campaign_id_list:
                    campaign_count = db.api_order.count({'campaign_id': campaign_id})
                    campaignRank[db.api_campaign.find_one({'id': campaign_id})['title']] = campaign_count
                campaignRank = dict(sorted(campaignRank.items(), key=operator.itemgetter(1), reverse=True))

        return Response(campaignRank, status=status.HTTP_200_OK)

    #TODO rewrite campaign_id_list, caculating way 
    @action(detail=False, methods=['GET'], url_path=r'campaign_manage_order')
    @api_error_handler
    def seller_total_sales(self, request):
        api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search = Verify.PreOrderApi.FromSeller.verify(request)
        is_user = verify_seller_request(api_user)
        campaign_id, user_id = campaign.id, int(api_user.id)
        manage_order = {}

        if is_user:
            campaigns = db.api_campaign.find({'created_by_id': user_id})
            order_complete_count, order_proceed_count, pre_order_count, campaign_count = 0, 0, 0, 0
            campaign_id_list, total_order_uncheck_rate, total_order_close_rate, total_sales = [], 0, 0, 0
            
            for campaign_data in campaigns:
                order_complete_count = db.api_order.find({'campaign_id': campaign_data['id'], 'status': 'complete'}).count()
                order_proceed_count = db.api_order.find({'campaign_id': campaign_data['id'], 'status': 'review'}).count()
                pre_order_count = db.api_pre_order.find({'campaign_id': campaign_data['id']}).count()
                campaign_id_list.append(campaign_data['id'])
                
                try:
                    total_order_uncheck_rate += order_complete_count / (order_complete_count + order_proceed_count) * 100  
                except ZeroDivisionError:
                    total_order_uncheck_rate = 0
                try:      
                    total_order_close_rate += order_complete_count / (order_complete_count + pre_order_count) * 100
                except ZeroDivisionError:
                    total_order_close_rate = 0
                campaign_count += 1

            average_order_uncheck_rate, average_order_close_rate, average_sales, average_comment_count = 0, 0 , 0, 0
            try:
                average_order_uncheck_rate = total_order_uncheck_rate / campaign_count
            except ZeroDivisionError:
                average_order_uncheck_rate = 0
            try:
                average_order_close_rate = total_order_close_rate / campaign_count       
            except ZeroDivisionError:
                average_order_close_rate = 0

            order_datas = db.api_order.find({'campaign_id': {'$in': campaign_id_list}})
            for order_data in order_datas:
                for key, val in order_data['products'].items():
                    total_sales += val['subtotal']
            try:   # 總campaign完成訂單總金額平均
                average_sales = total_sales / campaign_count
            except ZeroDivisionError:
                average_sales = 0
            try:
                average_comment_count = db.api_campaign_comment.find({'campaign_id': {'$in': campaign_id_list}}).count() / campaign_count
            except ZeroDivisionError:
                average_comment_count = 0

            # manage order
            pre_order_qty, order_qty, close_rate, uncheckout_rate, complete_sales, comment_count = 0, 0, 0, 0, 0, 0
            pre_order_datas = db.api_pre_order.find({'campaign_id': campaign_id})
            for pre_order_data in pre_order_datas:
                for key, val in pre_order_data['products'].items():
                    pre_order_qty += val['qty']
            order_datas = db.api_order.find({'campaign_id': campaign_id, 'status': 'complete'})
            for order_data in order_datas:
                for key, val in order_data['products'].items():
                    order_qty += val['qty']
            pre_order_count = db.api_pre_order.find({'campaign_id': campaign_id}).count()
            order_complete_count = db.api_order.find({'campaign_id': campaign_id, 'status': 'complete'}).count()
            order_proceed_count = db.api_order.find({'campaign_id': campaign_id, 'status': 'review'}).count()
            order_datas = db.api_order.find({'campaign_id': campaign_id, 'status': 'complete'})
            comment_count = db.api_campaign_comment.find({'campaign_id': campaign_id}).count()
            for order_data in order_datas:
                for key, val in order_data['products'].items():
                    # 完成訂單總金額
                    complete_sales += val['subtotal']
            close_rate, uncheckout_rate = 0, 0
            # 訂單成交量
            try:
                close_rate = order_complete_count / (order_complete_count + pre_order_count) * 100
            except ZeroDivisionError:
                close_rate = 0
            # 未完成付款
            try:
                uncheckout_rate = order_proceed_count / (order_complete_count + order_proceed_count) * 100
            except ZeroDivisionError:
                uncheckout_rate = 0
            
            manage_order['close_rate'] = close_rate
            manage_order['complete_sales'] = complete_sales
            manage_order['uncheckout_rate'] = uncheckout_rate
            manage_order['comment_count'] = comment_count
            manage_order['cart_qty'] = (pre_order_count + order_proceed_count)
            manage_order['order_qty'] = order_complete_count
            manage_order['close_rate_raise'] = close_rate - average_order_close_rate
            manage_order['uncheckout_rate_raise'] = uncheckout_rate - average_order_uncheck_rate
            try:
                manage_order['campaign_sales_raise'] = complete_sales / average_sales
            except ZeroDivisionError:
                manage_order['campaign_sales_raise'] = 0
            try:
                manage_order['comment_count_raise'] = comment_count / average_comment_count
            except ZeroDivisionError:
                manage_order['comment_count_raise'] = 0

        return Response(manage_order, status=status.HTTP_200_OK)
                
    
    @action(detail=False, methods=['GET'], url_path=r'order_list')
    @api_error_handler
    def get_merge_order_list(self, request):

        api_user, platform_id, platform_name, campaign_id, search, page=getparams(request, ('platform_id', 'platform_name', 'campaign_id', 'search', 'page'))

        Verify.verify_user(api_user)
        platform = Verify.get_platform(api_user, platform_name, platform_id)
        campaign = Verify.get_campaign_from_platform(platform, campaign_id)

        pre_orders_queryset = campaign.pre_orders.exclude(subtotal=0).order_by('created_at')

        orders_queryset = campaign.orders.all().order_by('created_at')
        # if search:
        #     if search.isnumeric():
        #         pre_orders_queryset = pre_orders_queryset.filter(Q(id=int(search)) | Q(customer_name__icontains=search) | Q(phone__icontains=search))
        #         orders_queryset = orders_queryset.filter(Q(id=int(search)) | Q(customer_name__icontains=search) | Q(phone__icontains=search))
        #     else:
        #         pre_orders_queryset = pre_orders_queryset.filter(Q(customer_name__icontains=search) | Q(phone__icontains=search))
        #         orders_queryset = orders_queryset.filter(Q(id=int(search)) | Q(customer_name__icontains=search) | Q(phone__icontains=search))


        # pre_order_paginator = Paginator(pre_orders_queryset, 10) # Show 25 contacts per page.
        # pre_order_list = pre_order_paginator.get_page(page)

        # order_paginator = Paginator(pre_orders_queryset, 10)
        # order_list = order_paginator.get_page(page)

        merge_list=[]

        order_index=0
        pre_order_index=0
        try:
            if orders_queryset[0] and pre_orders_queryset[0]:
                for i in range(len(pre_orders_queryset)+len(orders_queryset)):
                    if orders_queryset[order_index].created_at>=pre_orders_queryset[pre_order_index].created_at:
                        
                        merge_list.append({"type":"order","data":OrderSerializer(orders_queryset[order_index]).data})
                        order_index+=1
                    else:
                        # if not pre_orders_queryset[pre_order_index].products:
                        #     continue
                        merge_list.append({"type":"pre_order","data":PreOrderSerializer(pre_orders_queryset[pre_order_index]).data})
                        pre_order_index+=1
        except IndexError:
            pass
        
        if order_index==len(orders_queryset):
            for i in range(pre_order_index,len(pre_orders_queryset)):
                # if not pre_orders_queryset[pre_order_index].products:
                #             continue
                merge_list.append({"type":"pre_order","data":PreOrderSerializer(pre_orders_queryset[pre_order_index]).data})
                pre_order_index+=1

        else:
            for i in range(order_index,len(orders_queryset)):
                merge_list.append({"type":"order","data":OrderSerializer(orders_queryset[order_index]).data})
                order_index+=1

        

        return Response(merge_list, status=status.HTTP_200_OK)
            

    @action(detail=False, methods=['GET'], url_path=r'edit_allow_checkout')
    @api_error_handler
    def campaign_edit_allow_checkout(self, request):

        api_user, platform_id, platform_name, campaign_id, _status=getparams(request, ('platform_id', 'platform_name', 'campaign_id', 'status'))

        Verify.verify_user(api_user)
        platform = Verify.get_platform(api_user, platform_name, platform_id)
        campaign = Verify.get_campaign_from_platform(platform, campaign_id)

        campaign.meta['allow_checkout']=1 if int(_status) else 0
        campaign.save()

        return Response({"allow_checkout":campaign.meta['allow_checkout']}, status=status.HTTP_200_OK)
