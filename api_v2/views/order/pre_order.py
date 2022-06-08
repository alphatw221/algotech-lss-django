from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from api import models
from django.db.models import Q
from api.utils.common.order_helper import PreOrderHelper
import lib


class PreOrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PreOrderViewSet(viewsets.ModelViewSet):
    queryset = models.order.pre_order.PreOrder.objects.all().order_by('id')
    serializer_class = models.order.pre_order.PreOrderSerializer
    filterset_fields = []
    pagination_class = PreOrderPagination


# ---------------------------------------------- buyer ------------------------------------------------------

    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_pre_order(self, request, pk=None):
        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, campaign, save=True)

        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)
      
      
    @action(detail=True, methods=['PUT'], url_path=r'delivery', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_delivery_info(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        method, shipping_option = \
            lib.util.getter.getdata(request, ( "method", "shipping_option"), required=True)
        delivery_info, pickup_info = \
            lib.util.getter.getdata(request, ("delivery_info", "pickup_info"), required=False)

        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)

        

        serializer = models.order.pre_order.PreOrderSerializerUpdateDelivery(pre_order, data=delivery_info, partial=True) \
            if method=='delivery' else models.order.pre_order.PreOrderSerializerUpdatePickup(pre_order, data=pickup_info, partial=True)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pre_order = serializer.save()
        
        pre_order.shipping_method = method
        # pre_order.save()   #make sure this line is necessary
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, campaign, shipping_option, save=True)

        #checkout

        api_order = PreOrderHelper.checkout(api_user, pre_order)
        order = lib.util.verify.Verify.get_order(api_order['id'])


        return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'buyer/add', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def buyer_add_order_product(self, request, pk=None):
        api_user, campaign_product_id, qty = lib.util.getter.getparams(request, ('campaign_product_id', 'qty',), with_user=True, seller=False)

        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id)

        PreOrderHelper.add_product(api_user, pre_order, campaign_product, qty)
        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)

# ---------------------------------------------- seller ------------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'seller/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_list_pre_order(self, request):

        api_user, campaign_id, search = lib.util.getter.getparams(request, ('campaign_id', 'search'), with_user=True, seller=True)

        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        print (user_subscription.campaigns.filter(id='452'))
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        queryset = campaign.pre_orders.exclude(subtotal=0).order_by('id')

        if search:
            if search.isnumeric():
                queryset = queryset.filter(
                    Q(id=int(search)) | Q(customer_name__icontains=search) | Q(phone__icontains=search))
            else:
                queryset = queryset.filter(Q(customer_name__icontains=search) | Q(phone__icontains=search))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = models.order.pre_order.PreOrderSerializer(page, many=True)
            result = self.get_paginated_response(
                serializer.data)
            data = result.data
        else:
            serializer = models.order.pre_order.PreOrderSerializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)