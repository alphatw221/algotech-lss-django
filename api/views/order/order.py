from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from api.models.order.pre_order import PreOrder, PreOrderSerializer
from api.models.order.order import Order, OrderSerializer, OrderSerializerUpdatePayment, OrderSerializerUpdateShipping
import json, pendulum

from rest_framework.response import Response
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from rest_framework.pagination import PageNumberPagination
from django.db import transaction

import functools


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
    if not api_user:
        raise ApiVerifyError("no user found")
    elif api_user.status != "valid":
        raise ApiVerifyError("not activated user")
    if not api_user.order.filter(id=order_id).exists():
        raise ApiVerifyError("not pre_order found")
    if check_info == None:
        return api_user.order.get(id=order_id)

    order = OrderSerializer.objects.get(id=order_id)
    if not order.payment_first_name:
        raise ApiVerifyError("no payment first name")
    if not order.payment_last_name:
        raise ApiVerifyError("no payment last name")
    if not order.payment_company:
        raise ApiVerifyError("no payment company")
    if not order.payment_postcode:
        raise ApiVerifyError("no payment post code")
    if not order.payment_region:
        raise ApiVerifyError("no payment region")
    if not order.payment_location:
        raise ApiVerifyError("no payment location")
    if not order.payment_address_1:
        raise ApiVerifyError("no payment address")
    return api_user.order.get(id=order_id)


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
        api_user = request.user.api_users.get(type='customer')

        order = verify_buyer_request(
            api_user, order_id=pk)

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'buyer_info')
    @api_error_handler
    def update_buyer_order_info(self, request, pk=None):
        api_user = request.user.api_users.get(type='customer')

        order = verify_buyer_request(
            api_user, order_id=pk)
        
        serializer = OrderSerializerUpdatePayment(order, data=request.data, partial=True)
        if not serializer.is_valid():
            pass
        serializer = OrderSerializerUpdateShipping(order, data=request.data, partial=True)
        if not serializer.is_valid():
            pass

        order = serializer.save()
        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path=r'buyer_submit')
    @api_error_handler
    def buyer_update_delivery_payment_info(self, request, pk=None):
        api_user = request.user.api_users.get(type='customer')

        order = verify_buyer_request(
            api_user, order_id=pk, check_info=True)
        
        request.data['status'] = 'unpaid'
        serializer = OrderSerializerUpdatePayment(order, data=request.data, partial=True)
        if not serializer.is_valid():
            pass

        order = serializer.save()
        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path=r'buyer_complete')
    @api_error_handler
    def buyer_complete_order(self, request, pk=None):
        api_user = request.user.api_users.get(type='customer')

        order = verify_buyer_request(
            api_user, order_id=pk, check_info=True)
        
        request.data['paid_at'] = pendulum.now()
        serializer = OrderSerializerUpdatePayment(order, data=request.data, partial=True)
        if not serializer.is_valid():
            pass

        order = serializer.save()
        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'buyer_cancel')
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
    def cancel(cls, api_user, order):
        # cls._check_lock(api_user, order)
        with transaction.atomic():
            serializer = PreOrderSerializer(
                data=OrderSerializer(order).data)
            if not serializer.is_valid():
                pass
            pre_order = serializer.save()

            for order_product in order.order_products.all():
                order_product.order = None
                order_product.pre_order = pre_order.id
                order_product.save()

            order.products = {}
            order.total = 0
            order.subtotal = 0
            order.status = 'staging'
            order.save()

        return pre_order
