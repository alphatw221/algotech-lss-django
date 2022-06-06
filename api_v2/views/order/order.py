from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes
from rest_framework.parsers import MultiPartParser

from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile

from api import models
from api.utils.common.order_helper import PreOrderHelper
import lib


class OrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.order.order.Order.objects.all().order_by('id')
    pagination_class = OrderPagination


    @action(detail=True, methods=['GET'], url_path=r'buyer/retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_order(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_customer_user(request)
        order = lib.util.verify.Verify.get_order_by_api_user(api_user, pk)

        return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['PUT'], url_path=r'buyer/receipt/upload', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_upload_receipt(self, request, pk):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        order = lib.util.verify.Verify.get_order_by_api_user(api_user, pk)

        last_five_digit, image, =lib.util.getter.getdata(request,('last_five_digit', 'image'), required=False)
        
        if image and image != "undefined":
            image_path = default_storage.save(
                f'campaign/{order.campaign.id}/order/{order.id}/receipt/{image.name}', 
                ContentFile(image.read())
            )
            order.meta["receipt_image"] = settings.GS_URL + image_path

        if last_five_digit:
            order.meta["last_five_digit"] = last_five_digit

        order.payment_method = "Direct Payment"
        order.status = "complete"
        order.save()
        # send_email(order_id)
        # shop, order, campaign = confirmation_email_info(order_id)
        # sib_service.transaction_email.OrderConfirmationEmail(shop=shop, order=order, campaign=campaign, to=[order.get('shipping_email')], cc=[]).send()

        return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'buyer/history', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_buyer_order_history(self, request):

        api_user = lib.util.verify.Verify.get_customer_user(request)

        page = self.paginate_queryset(api_user.orders.all())
        if page is not None:
            serializer = models.order.order.OrderSerializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            data = models.order.order.OrderSerializer(api_user.orders, many=True).data

        return Response(data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['GET'], url_path=r'buyer/retrieve/state', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_buyer_order_state(self, request, pk):
        api_user = lib.util.verify.Verify.get_customer_user(request)
        order = lib.util.verify.Verify.get_order_by_api_user(api_user, pk)

        return Response(order.status, status=status.HTTP_200_OK)