from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from api import models
from api import utils

import lib, io


class PreOrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PreOrderViewSet(viewsets.ModelViewSet):
    queryset = models.order.pre_order.PreOrder.objects.all().order_by('id')
    serializer_class = models.order.pre_order.PreOrderSerializer
    filterset_fields = []
    pagination_class = PreOrderPagination


    @action(detail=True, methods=['GET'], url_path=r'buyer_retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_pre_order(self, request, pk=None):
        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)
        
        price_detail = utils.common.order_helper.PreOrderHelper.count_buyer_pre_order_detail(pre_order, campaign)
        
        serializer = models.order.pre_order.PreOrderSerializer(pre_order)
        json_pre_order = JSONRenderer().render(serializer.data)
        stream = io.BytesIO(json_pre_order)
        json_pre_order = JSONParser().parse(stream)
        json_pre_order['pre_order_price_detail'] = price_detail

        return Response(json_pre_order, status=status.HTTP_200_OK)