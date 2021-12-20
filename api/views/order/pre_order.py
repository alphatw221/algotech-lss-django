from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign_product import CampaignProduct
from api.models.order.pre_order import PreOrder, PreOrderSerializer
from api.models.order.order import Order, OrderSerializer, OrderSerializerUpdateShipping

from rest_framework.response import Response
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError, platform_dict
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import F

from api.models.order.order_product import OrderProduct, OrderProductSerializer
from django.conf import settings

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


def verify_buyer_request(api_user, pre_order_id, platform_name=None, order_product_id=None, campaign_product_id=None):
    if not api_user:
        raise ApiVerifyError("no user found")
    elif api_user.status != "valid":
        raise ApiVerifyError("not activated user")
    if not api_user.pre_orders.filter(id=pre_order_id).exists():
        raise ApiVerifyError("not pre_order found")
    pre_order = api_user.pre_orders.get(id=pre_order_id)

    if platform_name:
        if platform_name not in platform_dict:
            raise ApiVerifyError("no platfrom name found")
    if order_product_id:
        if not pre_order.order_products.filter(id=order_product_id).exists():
            raise ApiVerifyError("no order_product found")
        order_product = pre_order.order_products.select_for_update().get(
            id=order_product_id)
        campaign_product = CampaignProduct.objects.select_for_update().get(
            id=order_product.campaign_product.id)
        return pre_order, campaign_product, order_product

    if campaign_product_id:
        if not pre_order.campaign.products.filter(id=campaign_product_id).exists():
            raise ApiVerifyError("no campaign_product found")
        campaign_product = pre_order.campaign.products.select_for_update().get(
            id=campaign_product_id)
        return pre_order, campaign_product

    return pre_order


def verify_seller_request(api_user, platform_name, platform_id, campaign_id, pre_order_id=None, order_product_id=None, campaign_product_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)

    if pre_order_id:
        if not campaign.pre_orders.filter(id=pre_order_id).exists():
            raise ApiVerifyError('no pre_order found')
        pre_order = campaign.pre_orders.get(id=pre_order_id)

        if order_product_id:
            if not pre_order.order_products.filter(id=order_product_id).exists():
                raise ApiVerifyError("no order_product found")
            order_product = pre_order.order_products.select_for_update().get(
                id=order_product_id)
            campaign_product = CampaignProduct.objects.select_for_update().get(
                id=order_product.campaign_product.id)
            return platform, campaign, pre_order, campaign_product, order_product

        if campaign_product_id:
            if not pre_order.campaign.products.filter(id=campaign_product_id).exists():
                raise ApiVerifyError("no campaign_product found")
            campaign_product = pre_order.campaign.products.select_for_update().get(
                id=campaign_product_id)
            return platform, campaign, pre_order, campaign_product

        return platform, campaign, pre_order

    return platform, campaign


class PreOrderPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PreOrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = PreOrder.objects.all().order_by('id')
    serializer_class = PreOrderSerializer
    filterset_fields = []

    @action(detail=True, methods=['GET'], url_path=r'seller_retrieve')
    @api_error_handler
    def seller_retrieve_pre_order(self, request, pk=None):
        api_user, platform_id, platform_name, campaign_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id"))

        _, _, pre_order = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

        serializer = PreOrderSerializer(pre_order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller_list')
    @api_error_handler
    def seller_list_pre_order(self, request):
        api_user, platform_id, platform_name, campaign_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id"))

        _, campaign = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id)

        queryset = campaign.pre_orders.all()
        # TODO filtering
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PreOrderSerializer(page, many=True)
            result = self.get_paginated_response(
                serializer.data)
            data = result.data
        else:
            serializer = PreOrderSerializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_checkout')
    @api_error_handler
    def seller_pre_order_checkout(self, request, pk=None):

        api_user, platform_id, platform_name, campaign_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id"))

        _, _, pre_order = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

        order = PreOrderHelper.checkout(api_user, pre_order)

        return Response('test', status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_add')
    @api_error_handler
    def seller_add_order_product(self, request, pk=None):
        api_user, platform_id, platform_name, campaign_id, campaign_product_id, qty, customer_id, customer_name = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "campaign_product_id", "qty", "customer_id", "customer_name"))

        _, _, pre_order, campaign_product = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk, campaign_product_id=campaign_product_id)

        order_product = PreOrderHelper.add_product(
            api_user, pre_order, campaign_product, qty, platform_name, customer_id, customer_name)

        return Response('test', status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_update')
    @api_error_handler
    def seller_update_order_product(self, request, pk=None):

        api_user, platform_id, platform_name, campaign_id, order_product_id, qty = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "order_product_id", "qty"))

        _, _, pre_order, campaign_product, order_product = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk, order_product_id=order_product_id)

        order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, campaign_product, qty)
        return Response('test', status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_retrieve')
    @api_error_handler
    def buyer_retrieve_pre_order(self, request, pk=None):
        api_user = request.user.api_users.get(type='customer')
        pre_order = verify_buyer_request(
            api_user, pre_order_id=pk)

        serializer = PreOrderSerializer(pre_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'buyer_checkout')
    @api_error_handler
    def buyer_pre_order_checkout(self, request, pk=None):

        api_user = request.user.api_users.get(type='customer')

        pre_order = verify_buyer_request(
            api_user, pre_order_id=pk)
        order = PreOrderHelper.checkout(api_user, pre_order)

        return Response('test', status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_add')
    @api_error_handler
    def buyer_add_order_product(self, request, pk=None):
        api_user, campaign_product_id, platform_name, customer_id, customer_name, qty = getparams(
            request, ("campaign_product_id", "platform_name", "customer_id", "customer_name", "qty"), seller=False)

        pre_order, campaign_product = verify_buyer_request(
            api_user, pk, platform_name=platform_name, campaign_product_id=campaign_product_id)

        order_product = PreOrderHelper.add_product(
            api_user, pre_order, campaign_product, qty, platform_name, customer_id, customer_name)

        return Response('test', status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_update')
    @api_error_handler
    def buyer_update_order_product(self, request, pk=None):
        api_user, order_product_id, qty = getparams(
            request, ("order_product_id", "qty"), seller=False)

        pre_order, campaign_product, order_product = verify_buyer_request(
            api_user, pk, order_product_id=order_product_id)

        order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, campaign_product, qty)

        return Response('test', status=status.HTTP_200_OK)


class PreOrderHelper():

    class PreOrderValidator():
        pass

    @classmethod
    def update_product(cls, api_user, pre_order, order_product, campaign_product, qty):
        cls._check_lock(api_user, pre_order)
        cls._check_qty(campaign_product, qty)
        qty_difference = cls._check_stock(
            campaign_product, original_qty=order_product.qty, request_qty=qty)

        with transaction.atomic():
            campaign_product.qty_sold = campaign_product.qty_sold+qty_difference
            order_product.qty = qty
            pre_order.products[str(order_product.id)]['qty'] = qty
            pre_order.total = pre_order.total + \
                (qty_difference*campaign_product.price)
            pre_order.lock_at = datetime.now()
            campaign_product.save()
            order_product.save()
            pre_order.save()

        return order_product

    @classmethod
    def add_product(cls, api_user, pre_order, campaign_product, qty, platform, customer_id, customer_name):

        cls._check_lock(api_user, pre_order)
        cls._check_qty(campaign_product, qty)
        cls._check_addable(pre_order, campaign_product)
        qty_difference = cls._check_stock(
            campaign_product, original_qty=0, request_qty=qty)
        cls._check_platform(platform, customer_id, customer_name)

        with transaction.atomic():
            order_product = OrderProduct.objects.select_for_update().create(campaign=campaign_product.campaign,
                                                                            campaign_product=campaign_product,
                                                                            pre_order=pre_order,
                                                                            qty=qty,
                                                                            customer_id=customer_id,
                                                                            customer_name=customer_name,
                                                                            platform=platform, type=campaign_product.type)
            order_product.save()

            campaign_product.qty_sold = campaign_product.qty_sold+qty_difference
            campaign_product.save()

            pre_order.products.update(
                {str(order_product.id): {"price": campaign_product.price, "qty": qty}})
            pre_order.total = pre_order.total + \
                (qty_difference*campaign_product.price)
            pre_order.lock_at = datetime.now()
            pre_order.save()

        return order_product

    @classmethod
    def checkout(cls, api_user, pre_order):
        cls._check_lock(api_user, pre_order)
        with transaction.atomic():
            serializer = OrderSerializer(
                data=PreOrderSerializer(pre_order).data)
            if not serializer.is_valid():
                pass
            order = serializer.save()

            for order_product in pre_order.order_products.all():
                order_product.pre_order = None
                order_product.order = order.id
                order_product.save()

            pre_order.products = {}
            pre_order.total = 0
            pre_order.subtotal = 0
            pre_order.save()

        return order

    @staticmethod
    def _check_platform(platform, customer_id, customer_name):
        pass

    @staticmethod
    def _check_lock(api_user, pre_order):
        pass

    @staticmethod
    def _check_qty(campaign_product, qty):
        pass

    @staticmethod
    def _check_stock(campaign_product, original_qty, request_qty):
        qty_difference = int(request_qty)-original_qty
        if qty_difference and campaign_product.qty_for_sale < qty_difference:
            raise ApiVerifyError("out of stock")
        return qty_difference

    @staticmethod
    def _check_addable(pre_order, campaign_product):
        pass
