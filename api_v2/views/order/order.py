from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser


from django.core.files.storage import default_storage
from django.conf import settings
from django.core.files.base import ContentFile


from api import models
import database
import lib

from automation import jobs

class OrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.order.order.Order.objects.all().order_by('id')
    pagination_class = OrderPagination

    # ----------------------------------------------- guest ----------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<order_oid>[^/.]+)/subscription', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_retrieve_order_with_user_subscription(self, request, order_oid):
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        return Response(models.order.order.OrderSerializerWithUserSubscription(order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<order_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_retrieve_order(self, request, order_oid):
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<order_oid>[^/.]+)/guest/receipt/upload', parser_classes=(MultiPartParser,), permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_upload_receipt(self, request, order_oid):

        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        last_five_digit, image, account_name =lib.util.getter.getdata(request,('last_five_digit', 'image', 'account_name'), required=False)

        if image not in [None, '', "undefined", 'null']:
            image_path = default_storage.save(
                f'campaign/{order.campaign.id}/order/{order.id}/receipt/{image.name}', 
                ContentFile(image.read())
            )
            order.meta["receipt_image"] = settings.GS_URL + image_path


        order.meta["last_five_digit"] = last_five_digit
        order.meta['account_name'] = account_name
        order.payment_method = "Direct Payment"
        order.status = "complete"
        order.save()

        content = lib.helper.order_helper.OrderHelper.get_confirmation_email_content(order)
        jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)     #queue this to redis if needed

        return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<order_oid>[^/.]+)/state', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_guest_order_state(self, request, order_oid):

        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        return Response(order.status, status=status.HTTP_200_OK)


    # ----------------------------------------------- buyer ----------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/(?P<order_oid>[^/.]+)/subscription', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_order_with_user_subscription(self, request, order_oid):
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        return Response(models.order.order.OrderSerializerWithUserSubscription(order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/(?P<order_oid>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_order(self, request, order_oid):

        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/latest/shipping', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_latest_order_shipping(self, request):
        api_user = lib.util.verify.Verify.get_customer_user(request)
        order = api_user.orders.last()

        return Response(models.order.order.OrderSerializerUpdateShipping(order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<order_oid>[^/.]+)/buyer/receipt/upload', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_upload_receipt(self, request, order_oid):

        # api_user = lib.util.verify.Verify.get_customer_user(request)
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        last_five_digit, image, account_name =lib.util.getter.getdata(request,('last_five_digit', 'image', 'account_name'), required=False)

        if image not in [None, '', "undefined", 'null']:
            image_path = default_storage.save(
                f'campaign/{order.campaign.id}/order/{order.id}/receipt/{image.name}', 
                ContentFile(image.read())
            )
            order.meta["receipt_image"] = settings.GS_URL + image_path


        order.meta["last_five_digit"] = last_five_digit
        order.meta['account_name'] = account_name
        order.payment_method = "Direct Payment"
        order.status = "complete"
        order.save()

        content = lib.helper.order_helper.OrderHelper.get_confirmation_email_content(order)
        jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)     #queue this to redis if needed

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
       

    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/(?P<order_oid>[^/.]+)/state', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def check_buyer_order_state(self, request, order_oid):

        order = lib.util.verify.Verify.get_order_with_oid(order_oid)

        return Response(order.status, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'buyer/retrieve/oid', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_order_oid(self, request, pk=None):
        
        api_user = lib.util.verify.Verify.get_customer_user(request)
        order = lib.util.verify.Verify.get_order_by_api_user(api_user,pk)
        oid = database.lss.order.get_oid_by_id(order.id)

        return Response(oid, status=status.HTTP_200_OK)
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
    

    @action(detail=True, methods=['GET'], url_path=r'seller/retrieve/oid', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_retrieve_order_oid(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        order = lib.util.verify.Verify.get_order(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, order.campaign.id)
        oid = database.lss.order.get_oid_by_id(order.id)

        return Response(oid, status=status.HTTP_200_OK)