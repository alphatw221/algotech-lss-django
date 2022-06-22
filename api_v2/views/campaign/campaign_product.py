from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from django.db.models import Q

from api import models
from api import utils

import lib


class CampaignProductPagination(PageNumberPagination):

    page_size = 25
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class CampaignProductViewSet(viewsets.ModelViewSet):
    queryset = models.campaign.campaign_product.CampaignProduct.objects.all().order_by('id')
    serializer_class = models.campaign.campaign_product.CampaignProductSerializer
    filterset_fields = []
    pagination_class = CampaignProductPagination

#----------------------------------------------guest--------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'guest/list', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_list(self, request):
        pre_order_oid = request.query_params.get('pre_order_oid')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        campaign_products = pre_order.campaign.products.filter(Q(type='product') | Q(type="product-fast"))
        
        return Response(models.campaign.campaign_product.CampaignProductSerializer(campaign_products, many=True).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'guest/cart/list', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_prodcut_list(self, request):
        pre_order_oid = request.query_params.get('pre_order_oid')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        
        return Response(models.campaign.campaign_product.CampaignProductSerializer(pre_order.campaign.products, many=True).data, status=status.HTTP_200_OK)

#----------------------------------------------buyer--------------------------------------------------


    @action(detail=False, methods=['GET'], url_path=r'buyer/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_list(self, request):
        pre_order_oid = request.query_params.get('pre_order_oid')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        campaign_products = pre_order.campaign.products.filter(Q(type='product') | Q(type="product-fast"))
        
        return Response(models.campaign.campaign_product.CampaignProductSerializer(campaign_products, many=True).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'buyer/cart/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_prodcut_list(self, request):
        pre_order_oid = request.query_params.get('pre_order_oid')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        
        return Response(models.campaign.campaign_product.CampaignProductSerializer(pre_order.campaign.products, many=True).data, status=status.HTTP_200_OK)