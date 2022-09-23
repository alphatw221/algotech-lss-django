from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes

from api import models
# from api.utils.common.order_helper import PreOrderHelper
import lib

class OrderProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.order.order_product.OrderProduct.objects.all().order_by('id')

    #------------------------------------------------- guest -------------------------------------------------------
    
    @action(detail=True, methods=['DELETE'], url_path=r'guest/delete', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def guest_delete_order_product(self, request, pk=None):

        pre_order_oid, = lib.util.getter.getparams(request, ('pre_order_oid',), with_user=False)
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)

        order_product = lib.util.verify.Verify.get_order_product(pk)

        lib.helper.order_helper.PreOrderHelper.delete_product(
            None, pre_order.id, order_product.id)

        pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, pre_order.campaign, save=True)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['PUT'], url_path=r'guest/update', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def guest_update_order_product(self, request, pk=None):

        pre_order_oid, qty = lib.util.getter.getparams(request, ('pre_order_oid', 'qty',), with_user=False)
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)

        order_product = lib.util.verify.Verify.get_order_product(pk)

        lib.helper.order_helper.PreOrderHelper.update_product(
            None, pre_order.id, order_product.id, qty)

        pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, pre_order.campaign, save=True)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)

    #------------------------------------------------- buyer -------------------------------------------------------

    @action(detail=True, methods=['DELETE'], url_path=r'buyer/delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def buyer_delete_order_product(self, request, pk=None):

        pre_order_oid, = lib.util.getter.getparams(request, ('pre_order_oid',), with_user=False)
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)

        api_user = lib.util.verify.Verify.get_customer_user(request)
        order_product = lib.util.verify.Verify.get_order_product(pk)

        lib.helper.order_helper.PreOrderHelper.delete_product(
            api_user, pre_order.id, order_product.id)

        pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, pre_order.campaign, save=True)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['PUT'], url_path=r'buyer/update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def buyer_update_order_product(self, request, pk=None):

        
        api_user, pre_order_oid, qty = lib.util.getter.getparams(request, ('pre_order_oid','qty',), with_user=True, seller=False)
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        order_product = lib.util.verify.Verify.get_order_product(pk)

        lib.helper.order_helper.PreOrderHelper.update_product(
            api_user, pre_order.id, order_product.id, qty)

        pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, pre_order.campaign, save=True)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)
    
    # ---------------------------------------------------------seller---------------------------------------------
    
    @action(detail=True, methods=['GET'], url_path=r'seller/delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def seller_delete_order_product(self, request, pk=None):

        api_user, pre_order_id = lib.util.getter.getparams(request, ('pre_order_id',), with_user=True, seller=True)

        pre_order = lib.util.verify.Verify.get_pre_order(pre_order_id)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)
        order_product = lib.util.verify.Verify.get_order_product_from_pre_order(pre_order, pk)

        lib.helper.order_helper.PreOrderHelper.delete_product(
            api_user, pre_order.id, order_product.id)

        pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, pre_order.campaign, save=True)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET'], url_path=r'seller/update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def seller_update_order_product(self, request, pk=None):
        api_user, pre_order_id,qty = lib.util.getter.getparams(request, ('pre_order_id', 'qty'), with_user=True, seller=True)

        pre_order = lib.util.verify.Verify.get_pre_order(pre_order_id)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)
        order_product = lib.util.verify.Verify.get_order_product_from_pre_order(pre_order, pk)

        lib.helper.order_helper.PreOrderHelper.update_product(
            api_user, pre_order.id, order_product.id, qty)

        pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, pre_order.campaign, save=True)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)

