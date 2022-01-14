from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from api.models.order.order import Order, OrderSerializer
from api.utils.common.verify import Verify
from api.utils.common.common import *

from backend.pymongo.mongodb import db
from dateutil.relativedelta import relativedelta
import datetime, operator

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler
from api.utils.common.common import getparams

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
    def seller_total_sales(self, request):
        api_user = request.user.api_users.get(type='user')
        is_user = verify_seller_request(api_user)
        total_sales = 0

        if is_user:
            user_id = api_user.id
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
                print (order_data['total'])
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
        
            total_pending = 1 - order_total / (pre_order_total + order_total)
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

    @action(detail=False, methods=['GET'], url_path=r'campaign_manage_order')
    @api_error_handler
    def seller_total_sales(self, request):
        api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search = Verify.PreOrderApi.FromSeller.verify(request)
        is_user = verify_seller_request(api_user)
        campaign_id = campaign.id
        
        manage_order = {}
        if is_user:
            pre_order_qty, order_qty, close_rate, uncheckout_rate, complete_sales, comment_count = 0, 0, 0, 0, 0, 0
            pre_order_datas = db.api_pre_order.find({'campaign_id': campaign_id})
            for pre_order_data in pre_order_datas:
                for key, val in pre_order_data['products'].items():
                    pre_order_qty += val['qty']
            order_datas = db.api_order.find({'campaign_id': campaign_id, 'status': 'complete'})
            for order_data in order_datas:
                for key, val in order_data['products'].items():
                    order_qty += val['qty']
            # 商品數量成交量
            # close_rate = order_qty / (order_qty + pre_order_qty)
            pre_order_count = db.api_pre_order.find({'campaign_id': campaign_id}).count()
            order_complete_count = db.api_order.find({'campaign_id': campaign_id, 'status': 'complete'}).count()
            order_proceed_count = db.api_order.find({'campaign_id': campaign_id, 'status': 'proceed'}).count()
            order_datas = db.api_order.find({'campaign_id': campaign_id, 'status': 'complete'})
            comment_count = db.api_campaign_comment.find({'campaign_id': campaign_id}).count()
            for order_data in order_datas:
                for key, val in order_data['products'].items():
                    # 完成訂單總金額
                    complete_sales += val['subtotal']
            # 訂單成交量
            close_rate = order_complete_count / (order_complete_count + pre_order_count) * 100
            # 未完成付款
            uncheckout_rate = order_proceed_count / (order_complete_count + order_proceed_count) * 100
            
            manage_order['close_rate'] = close_rate
            manage_order['complete_sales'] = complete_sales
            manage_order['uncheckout_rate'] = uncheckout_rate
            manage_order['comment_count'] = comment_count
            manage_order['cart_qty'] = pre_order_qty
            manage_order['order_qty'] = order_qty

        return Response(manage_order, status=status.HTTP_200_OK)
                
                
                
                
            