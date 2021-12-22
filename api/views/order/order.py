from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from api.models.order.pre_order import PreOrder, PreOrderSerializer
from api.models.order.order import Order, OrderSerializer, OrderSerializerUpdatePaymentShipping
import json, pendulum

from rest_framework.response import Response
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from rest_framework.pagination import PageNumberPagination
from django.db import transaction

import functools
from backend.pymongo.mongodb import db, client


def getparams(request, params: tuple, seller=True):
    ret = [request.user.api_users.get(type='user')] if seller else [
        request.user.api_users.get(type='customer')]
    for param in params:
        ret.append(request.query_params.get(param))
    return ret


def api_error_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiVerifyError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     print(e)
        #     return Response({"message": str(datetime.now())+"server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return wrapper


def verify_buyer_request(api_user, order_id, check_info=None):
    print (api_user.id)
    if not api_user:
        raise ApiVerifyError("no user found")
    elif api_user.status != "valid":
        raise ApiVerifyError("not activated user")
    if not Order.objects.get(customer_id=api_user.id):
        raise ApiVerifyError("not customer's order found")
    if check_info == None:
        return Order.objects.get(customer_id=api_user.id, id=order_id)
    
    verify_message = {}
    check_exist = False
    #TODO 訊息彙整回傳一次
    order = Order.objects.get(customer_id=api_user.id, id=order_id)
    if not order.shipping_first_name:
        check_exist = True
        verify_message['shipping_first_name'] = 'not valid'
    if not order.shipping_last_name:
        check_exist = True
        verify_message['shipping_last_name'] = 'not valid'
    if not order.shipping_phone:
        check_exist = True
        verify_message['shipping_phone'] = 'not valid'
    if not order.shipping_postcode:
        check_exist = True
        verify_message['shipping_postcode'] = 'not valid'
    if not order.shipping_region:
        check_exist = True
        verify_message['shipping_region'] = 'not valid'
    if not order.shipping_location:
        check_exist = True
        verify_message['shipping_location'] = 'not valid'
    if not order.shipping_address_1:
        check_exist = True
        verify_message['shipping_address'] = 'not valid'
    if not order.shipping_method:
        check_exist = True
        verify_message['shipping_method'] = 'not valid'
    if not order.payment_first_name:
        check_exist = True
        verify_message['payment_first_name'] = 'not valid'
    if not order.payment_last_name:
        check_exist = True
        verify_message['payment_last_name'] = 'not valid'
    if not order.payment_company:
        check_exist = True
        verify_message['payment_company'] = 'not valid'
    if not order.payment_postcode:
        check_exist = True
        verify_message['payment_postcode'] = 'not valid'
    if not order.payment_region:
        check_exist = True
        verify_message['payment_region'] = 'not valid'
    if not order.payment_location:
        check_exist = True
        verify_message['payment_location'] = 'not valid'
    if not order.payment_address_1:
        check_exist = True
        verify_message['payment_address'] = 'not valid'
    if check_exist == True:
        raise ApiVerifyError(verify_message)
    return order


def verify_seller_request(api_user, platform_name, platform_id, campaign_id, order_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)

    if order_id:
        if not campaign.order.filter(id=order_id).exists():
            raise ApiVerifyError('no campaign product found')
        order = campaign.order.get(id=order_id)
        return platform, campaign, order

    return platform, campaign


class OrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all().order_by('id')
    serializer_class = OrderSerializer
    filterset_fields = []
    
    @action(detail=True, methods=['GET'], url_path=r'seller_retrieve')
    @api_error_handler
    def seller_retrieve_order(self, request, pk=None):
        api_user, platform_id, platform_name, campaign_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id"))

        _, _, order = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, order_id=pk)

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'seller_list')
    @api_error_handler
    def seller_list_order(self, request):
        api_user, platform_id, platform_name, campaign_id, order_by = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "order_by"))

        _, campaign = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id)

        queryset = campaign.order.all()
        # TODO filtering
        if order_by:
            queryset = queryset.order_by(order_by)
        
        page = OrderPagination.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            result = OrderPagination.get_paginated_response(
                serializer.data)
            data = result.data
        else:
            serializer = OrderSerializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'buyer_retrieve')
    @api_error_handler
    def buyer_retrieve_order(self, request, pk=None):
        # 先檢查exists 才給request get
        api_user = request.user.api_users.get(type='customer')

        order = verify_buyer_request(
            api_user, order_id=pk)

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'buyer_submit')
    @api_error_handler
    def update_buyer_order_info(self, request, pk=None):
        api_user = request.user.api_users.get(type='customer')

        order = verify_buyer_request(
            api_user, order_id=pk)
        
        request.data['status'] = 'unpaid'
        serializer = OrderSerializerUpdatePaymentShipping(order, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        order = verify_buyer_request(
            api_user, order_id=pk, check_info=True)
        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # @action(detail=True, methods=['GET'], url_path=r'buyer_complete')
    # @api_error_handler
    # def buyer_complete_order(self, request, pk=None):
    #     api_user = request.user.api_users.get(type='customer')

    #     order = verify_buyer_request(
    #         api_user, order_id=pk, check_info=True)
        
    #     request.data['paid_at'] = pendulum.now()
    #     request.data['status'] = 'paid'
    #     serializer = OrderSerializerUpdatePaymentShipping(order, data=request.data, partial=True)
    #     if not serializer.is_valid():
    #         pass

    #     order = serializer.save()
    #     serializer = OrderSerializer(order)

    #     return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_cancel')
    @api_error_handler
    def buyer_cancel_order(self, request, pk=None):
        api_user = request.user.api_users.get(type='customer')

        order = verify_buyer_request(
            api_user, order_id=pk, check_info=True)
        
        pre_order = OrderHelper.cancel(api_user, order)

        return Response('order canceled', status=status.HTTP_200_OK)


class OrderHelper():

    class OrderValidator():
        pass
    
    @classmethod
    def cancel(api_user, order):
        with client.start_session() as session:
            with session.start_transaction():
                api_order = db.order.find_one(
                    {'id': order.id}, session=session)
                
                campaign_id = api_order['campaign_id']
                customer_id = api_order['customer_id']
                pre_order_id = db.api_pre_order.find_one({'campaign_id': campaign_id, 'customer_id': customer_id})['id']
                
                products_dict = {}
                total_count = 0
                order_products = db.api_order_product.find({'campaign_id': campaign_id, 'customer_id': customer_id, 'order_id': order.id})
                for order_product in order_products:
                    campaign_product_id = order_product['campaign_product_id']
                    price = db.api_campaign_product.find_one({'id': campaign_product_id})['price']
                    product_dict = {}

                    if db.api_order_product.find({'pre_order_id': pre_order_id, 'order_id': None, 'campaign_product_id': campaign_product_id}).count() > 0:
                        pre_order_product = db.api_order_product.find_one({'pre_order_id': pre_order_id, 'order_id': None, 'campaign_product_id': campaign_product_id})
                        
                        db.api_order_product.update_one(
                            {'pre_order_id': pre_order_id, 'campaign_product_id': campaign_product_id}, 
                            {'$set': 
                                {'qty': order_product['qty'] + pre_order_product['qty']}
                            }
                        )
                        db.api_order_product.delete_one({'order_id': order.id, 'campaign_product_id': campaign_product_id})

                        product_dict['qty'] = order_product['qty'] + pre_order_product['qty']
                        product_dict['price'] = price
                        total_count += (order_product['qty'] + pre_order_product['qty']) * price
                    else:
                        db.api_order_product.update_one(
                            {'pre_order_id': pre_order_id, 'campaign_product_id': campaign_product_id}, 
                            {'$set': 
                                {'qty': order_product['qty'], 'order_id': None}
                            }
                        )

                        product_dict['qty'] = order_product['qty']
                        product_dict['price'] = price
                        total_count += order_product['qty'] * price
                    products_dict[campaign_product_id] = product_dict
                
                db.api_pre_order.update_one(
                    {'id': pre_order_id},
                    {'$set': 
                        {'products': products_dict, 'total': total_count}
                    }
                )
                db.api_order.delete_one({'id': order.id})

        return pre_order_id
