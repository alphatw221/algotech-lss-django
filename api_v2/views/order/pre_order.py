from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


from api import models
from api import utils
from api.utils.common.verify import Verify
from api.models.order.pre_order import PreOrder, PreOrderSerializerUpdatePaymentShipping

import lib


class PreOrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PreOrderViewSet(viewsets.ModelViewSet):
    queryset = models.order.pre_order.PreOrder.objects.all().order_by('id')
    serializer_class = models.order.pre_order.PreOrderSerializer
    filterset_fields = []
    pagination_class = PreOrderPagination


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

        method, = \
            lib.util.getter.getdata(request, ( "method",), required=True)
        delivery_info, pickup_info = \
            lib.util.getter.getdata(request, ("delivery_info", "pickup_info"), required=False)

        pre_order = Verify.get_pre_order(pk)
        campaign = Verify.get_campaign_from_pre_order(pre_order)

        pre_order.shipping_method = method
        pre_order.save()   #make sure this line is necessary

        serializer = models.order.pre_order.PreOrderSerializerUpdateDelivery(pre_order, data=delivery_info, partial=True) \
            if method=='delivery' else models.order.pre_order.PreOrderSerializerUpdatePickup(pre_order, data=pickup_info, partial=True)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pre_order = serializer.save()
        
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order,campaign, save=True)

        return Response(PreOrderSerializerUpdatePaymentShipping(pre_order).data, status=status.HTTP_200_OK)
