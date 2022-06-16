from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import PageNumberPagination

from api.models.order.pre_order import PreOrder, PreOrderSerializer, PreOrderSerializerUpdatePaymentShipping
from api.utils.common.common import getdata, getparams
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError, platform_dict

from api.utils.common.order_helper import PreOrderHelper

from django.db.models import Q
import datetime
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler


class PreOrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PreOrderViewSet(viewsets.ModelViewSet):
    queryset = PreOrder.objects.all().order_by('id')
    serializer_class = PreOrderSerializer
    filterset_fields = []
    pagination_class = PreOrderPagination

    @action(detail=True, methods=['GET'], url_path=r'seller_retrieve', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def seller_retrieve_pre_order(self, request, pk=None):

        api_user = Verify.get_seller_user(request)
        pre_order = Verify.get_pre_order(pk)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)

        serializer = PreOrderSerializer(pre_order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller_list', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def seller_list_pre_order(self, request):

        api_user, campaign_id, search = getparams(request, ('campaign_id', 'search'), with_user=True, seller=True)

        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaign = Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        queryset = campaign.pre_orders.exclude(subtotal=0).order_by('id')

        if search:
            if search.isnumeric():
                queryset = queryset.filter(
                    Q(id=int(search)) | Q(customer_name__icontains=search) | Q(phone__icontains=search))
            else:
                queryset = queryset.filter(Q(customer_name__icontains=search) | Q(phone__icontains=search))

        if request.query_params.get('page'):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = PreOrderSerializer(page, many=True)
                result = self.get_paginated_response(
                    serializer.data)
                data = result.data
            else:
                serializer = PreOrderSerializer(queryset, many=True)
                data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_checkout', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def seller_pre_order_checkout(self, request, pk=None):

        api_user = Verify.get_seller_user(request)
        pre_order = Verify.get_pre_order(pk)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)

        api_order = PreOrderHelper.checkout(api_user, pre_order)
        return Response(api_order, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_add', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def seller_add_order_product(self, request, pk=None):
        api_user, campaign_product_id, qty = getparams(request, ('campaign_product_id', 'qty'), with_user=True,
                                                       seller=True)

        pre_order = Verify.get_pre_order(pk)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)

        campaign_product = Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id)
        api_order_product = PreOrderHelper.add_product(
            api_user, pre_order, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_update', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def seller_update_order_product(self, request, pk=None):
        api_user, order_product_id, qty = getparams(request, ('order_product_id', 'qty'), with_user=True, seller=True)

        pre_order = Verify.get_pre_order(pk)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)

        order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)
        api_order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'seller_adjust', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def seller_adjust(self, request, pk=None):

        adjust_price, adjust_title, free_delivery = getdata(request, ('adjust_price', 'adjust_title', 'free_delivery'))
        adjust_price = float(adjust_price)
        api_user = Verify.get_seller_user(request)
        pre_order = Verify.get_pre_order(pk)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)
        if type(free_delivery) != bool:
            raise ApiVerifyError("request data error")

        original_total = pre_order.total
        original_free_delivery = pre_order.free_delivery

        if pre_order.subtotal + adjust_price < 0:
            adjust_price = -pre_order.subtotal

        pre_order.adjust_price = adjust_price
        pre_order.free_delivery = free_delivery
        pre_order.adjust_title = adjust_title

        if free_delivery:
            pre_order.total = pre_order.subtotal + pre_order.adjust_price
        else:
            pre_order.total = pre_order.subtotal + pre_order.adjust_price + pre_order.shipping_cost

        seller_adjust_history = pre_order.history.get('seller_adjust', [])
        seller_adjust_history.append(
            {"original_total": original_total,
             "adjusted_total": pre_order.total,
             "original_free_delivery_status": original_free_delivery,
             "adjusted_free_delivery_status": pre_order.free_delivery,
             "adjusted_at": datetime.datetime.utcnow(),
             "adjusted_by": api_user.id
             }
        )
        pre_order.history['seller_adjust'] = seller_adjust_history

        pre_order.save()
        return Response(PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_delete', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def seller_delete_order_product(self, request, pk=None):

        api_user, order_product_id = getparams(request, ('order_product_id',), seller=True)

        pre_order = Verify.get_pre_order(pk)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)

        order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)
        PreOrderHelper.delete_product(
            api_user, pre_order, order_product)
        return Response({'message': "delete success"}, status=status.HTTP_200_OK)

    # ------------------buyer---------------------------------------------------------------------------

    from rest_framework.permissions import BasePermission

    class IsPreOrderCustomer(BasePermission):

        def has_permission(self, request, view):
            try:
                pk = view.kwargs.get('pk')
                api_user = Verify.get_customer_user(request)
                pre_order = Verify.get_pre_order(pk)
                Verify.user_match_pre_order(api_user, pre_order)
            except Exception:
                return False
            return True

    @action(detail=True, methods=['GET'], url_path=r'buyer_retrieve', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def buyer_retrieve_pre_order(self, request, pk=None):

        pre_order = Verify.get_pre_order(pk)
        serializer = PreOrderSerializer(pre_order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_checkout', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def buyer_pre_order_checkout(self, request, pk=None):

        api_user, = getparams(request, (), with_user=True, seller=False)
        pre_order = Verify.get_pre_order(pk)

        api_order = PreOrderHelper.checkout(api_user, pre_order)
        return Response(api_order, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_add', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def buyer_add_order_product(self, request, pk=None):

        api_user, campaign_product_id, qty = getparams(request, ('campaign_product_id', 'qty'), with_user=True,
                                                       seller=False)
        pre_order = Verify.get_pre_order(pk)
        campaign_product = Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id)

        api_order_product = PreOrderHelper.add_product(api_user, pre_order, campaign_product, qty)

        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_update', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def buyer_update_order_product(self, request, pk=None):

        api_user, order_product_id, qty = getparams(request, ('order_product_id', 'qty'), with_user=True, seller=False)
        pre_order = Verify.get_pre_order(pk)
        order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)

        api_order_product = PreOrderHelper.update_product(api_user,
                                                          pre_order, order_product, qty)

        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_delete', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def buyer_delete_order_product(self, request, pk=None):

        api_user, order_product_id, = getparams(request, ('order_product_id',), with_user=True, seller=False)
        pre_order = Verify.get_pre_order(pk)
        order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)

        PreOrderHelper.delete_product(
            api_user, pre_order, order_product)

        return Response({'message': "delete success"}, status=status.HTTP_200_OK)
