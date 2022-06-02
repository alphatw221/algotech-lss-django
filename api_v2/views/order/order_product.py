from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes

from api import models
from api.utils.common.order_helper import PreOrderHelper
import lib

class OrderProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.order.order_product.OrderProduct.objects.all().order_by('id')


    @action(detail=True, methods=['GET'], url_path=r'buyer/add', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def buyer_add_order_product(self, request, pk=None):
        api_user, campaign_product_id, qty = lib.util.getter.getparams(request, ('campaign_product_id', 'qty',), with_user=True, seller=False)

        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id)

        api_order_product = PreOrderHelper.add_product(api_user, pre_order, campaign_product, qty)

        return Response(api_order_product, status=status.HTTP_200_OK)


    @action(detail=True, methods=['DELETE'], url_path=r'buyer/delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def buyer_delete_order_product(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        order_product = lib.util.verify.Verify.get_order_product(pk)

        PreOrderHelper.delete_product(
            api_user, order_product.pre_order, order_product)

        pre_order = lib.util.verify.Verify.get_pre_order(order_product.pre_order.id)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['PUT'], url_path=r'buyer/update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def buyer_update_order_product(self, request, pk=None):
        api_user, qty = lib.util.getter.getparams(request, ('qty',), with_user=True, seller=False)

        order_product = lib.util.verify.Verify.get_order_product(pk)

        PreOrderHelper.update_product(
            api_user, order_product.pre_order, order_product, qty)

        pre_order = lib.util.verify.Verify.get_pre_order(order_product.pre_order.id)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)
