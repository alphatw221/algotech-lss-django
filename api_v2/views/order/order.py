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
from bson.json_util import loads, dumps
import database
import lib

from api.utils.advance_query.dashboard import get_campaign_merge_order_list_v2

from automation import jobs
from backend import pymongo,i18n
from api.utils.error_handle.error_handler.email_error_handler import email_error_handler

@email_error_handler
def send_shipping_email(order_id):

    order_data = pymongo.mongodb.db.api_order.find_one({'id': int(order_id)})
    campaign_id = order_data['campaign_id']
    campaign_data = pymongo.mongodb.db.api_campaign.find_one({'id': int(campaign_id)})
    facebook_page_id = campaign_data['facebook_page_id']
    shop_name = pymongo.mongodb.db.api_facebook_page.find_one({'id': int(facebook_page_id)})['name']
    customer_email = order_data['shipping_email']

    mail_subject = i18n.delivery_comfirm_mail.i18n_get_mail_subject(shop_name)
    mail_content = i18n.delivery_comfirm_mail.i18n_get_mail_content(order_id, campaign_data, order_data, shop_name)

    i18n.delivery_comfirm_mail.send_smtp_mail(customer_email, mail_subject, mail_content)

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
        last_five_digit, image, account_name, account_mode = lib.util.getter.getdata(request,('last_five_digit', 'image', 'account_name', 'account_mode'), required=False)

        if image not in [None, '', "undefined", 'null']:
            image_path = default_storage.save(
                f'campaign/{order.campaign.id}/order/{order.id}/receipt/{image.name}', 
                ContentFile(image.read())
            )
            order.meta["receipt_image"] = settings.GS_URL + image_path


        order.meta["last_five_digit"] = last_five_digit
        order.meta['account_name'] = account_name
        order.meta['account_mode'] = account_mode
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
        print('testing')
        order = api_user.orders.last()
        data = models.order.order.OrderSerializerUpdateShipping(order).data
        print(data)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<order_oid>[^/.]+)/buyer/receipt/upload', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_upload_receipt(self, request, order_oid):

        # api_user = lib.util.verify.Verify.get_customer_user(request)
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        last_five_digit, image, account_name, account_mode = lib.util.getter.getdata(request,('last_five_digit', 'image', 'account_name', 'account_mode'), required=False)

        if image not in [None, '', "undefined", 'null']:
            image_path = default_storage.save(
                f'campaign/{order.campaign.id}/order/{order.id}/receipt/{image.name}', 
                ContentFile(image.read())
            )
            order.meta["receipt_image"] = settings.GS_URL + image_path

        order.meta["last_five_digit"] = last_five_digit
        order.meta['account_name'] = account_name
        order.meta['account_mode'] = account_mode
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
    
    @action(detail=False, methods=['POST'], url_path=r'seller/order_list')
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_merge_order_list(self, request):

        api_user, campaign_id, search, page, page_size,order_status= lib.util.getter.getparams(request, ( 'campaign_id', 'search', 'page', 'page_size','status'),with_user=True, seller=True)
        f_payment,f_delivery,f_platform = lib.util.getter.getdata(request,('payment','delivery','platform'))
        
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)
        merge_list = get_campaign_merge_order_list_v2(campaign.id, search, order_status, f_payment, f_delivery, f_platform)
        count = len(merge_list)
        page,page_size = int(page),int(page_size)
        skip = (page-1)*page_size
        if len(merge_list) >= page_size:
            merge_list = merge_list[skip:skip+page_size]
        merge_list_str = dumps(merge_list)
        merge_list_json = loads(merge_list_str)

        return Response({'count':count,'data':merge_list_json}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path=r'seller/delivery_status', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_order_delivery_status(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        order = lib.util.verify.Verify.get_order(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, order.campaign.id)
        
        
        # content = i18n.delivery_comfirm_mail.i18n_get_mail_content(order)
        # jobs.send_email_job.send_email_job(order.campaign.title, order.shipping_email, content=content)
        
        # send_email(order.id)

        return Response(order, status=status.HTTP_200_OK)