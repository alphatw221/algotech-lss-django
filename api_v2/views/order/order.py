from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes
from rest_framework.parsers import MultiPartParser

from backend.pymongo.mongodb import db
from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile
from rsa import verify

# from api.utils.error_handle.error_handler.email_error_handler import email_error_handler
from api import utils
from api import models
import lib, service
sib_service = service.sendinblue


@utils.error_handle.error_handler.email_error_handler.email_error_handler
def confirmation_email_info(order_id):
    order = db.api_order.find_one({'id': int(order_id)})
    del order['_id']
    campaign_id = order['campaign_id']
    campaign = db.api_campaign.find_one({'id': int(campaign_id)})
    del campaign['_id']
    facebook_page_id = campaign['facebook_page_id']
    shop = db.api_facebook_page.find_one({'id': int(facebook_page_id)})['name']
    
    return shop, order, campaign

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

    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/latest/shipping', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_latest_order_shipping(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_customer_user(request)
        # order = lib.util.verify.Verify.get_order_by_api_user(api_user, pk)
        order = api_user.orders.last()

        return Response(models.order.order.OrderSerializerUpdateShipping(order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'buyer/receipt/upload', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_upload_receipt(self, request, pk):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        order = lib.util.verify.Verify.get_order_by_api_user(api_user, pk)

        last_five_digit, image, =lib.util.getter.getdata(request,('last_five_digit', 'image'), required=False)
        print(image)
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
        shop, order, campaign = confirmation_email_info(pk)
        sib_service.transaction_email.OrderConfirmationEmail(shop=shop, order=order, campaign=campaign, to=[order.get('shipping_email')], cc=[]).send()

        return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'buyer/history', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_buyer_order_history(self, request):

        api_user = lib.util.verify.Verify.get_customer_user(request)

        page = self.paginate_queryset(api_user.orders.all().order_by('-created_at'))
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
    
    # ------------------------------------seller----------------------------------------
    
    @action(detail=True, methods=['GET'], url_path=r'seller/retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_retrieve_order(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        order = lib.util.verify.Verify.get_order(pk)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, order.campaign.id)
        serializer = models.order.order.OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
