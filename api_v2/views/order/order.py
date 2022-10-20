from platform import platform
from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser


from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Q, Value


from api import models
import database
import lib
# import xlsxwriter


from automation import jobs
from api.utils.error_handle.error_handler.email_error_handler import email_error_handler
from api.utils.error_handle.error.api_error import ApiCallerError


class OrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = models.order.order.Order.objects.all().order_by('id')
    pagination_class = OrderPagination

    # ----------------------------------------------- guest ----------------------------------------------------
    # @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<order_oid>[^/.]+)/platform', permission_classes=(), authentication_classes=[])
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def guest_retrieve_order_platform(self, request, order_oid):
    #     order = lib.util.verify.Verify.get_order_with_oid(order_oid)
    #     return Response(order.platform, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<order_oid>[^/.]+)/subscription', permission_classes=(), authentication_classes=[])
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def guest_retrieve_order_with_user_subscription(self, request, order_oid):
    #     order = lib.util.verify.Verify.get_order_with_oid(order_oid)
    #     return Response(models.order.order.OrderSerializerWithUserSubscription(order).data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<order_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def guest_retrieve_order(self, request, order_oid):
    #     order = lib.util.verify.Verify.get_order_with_oid(order_oid)
    #     return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['PUT'], url_path=r'(?P<order_oid>[^/.]+)/guest/receipt/upload', url_name='guest_upload_receipt', parser_classes=(MultiPartParser,), permission_classes=(), authentication_classes=[])
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def guest_upload_receipt(self, request, order_oid):

    #     order = lib.util.verify.Verify.get_order_with_oid(order_oid)
    #     campaign = lib.util.verify.Verify.get_campaign_from_order(order)

    #     last_five_digit, image, account_name, account_mode = lib.util.getter.getdata(request,('last_five_digit', 'image', 'account_name', 'account_mode'), required=False)

    #     if image in [None, '', "undefined", 'null']:
    #         pass
    #     elif image.size > models.order.order.IMAGE_MAXIMUM_SIZE:
    #         raise lib.error_handle.error.api_error.ApiVerifyError('image_size_exceed_maximum_size')
    #     elif image.content_type not in models.order.order.IMAGE_SUPPORTED_TYPE:
    #         raise lib.error_handle.error.api_error.ApiVerifyError('not_support_this_image_type')
    #     else:
    #         try:
    #             image_name = image.name.replace(" ","")
    #             image_dir = f'campaign/{order.campaign.id}/order/{order.id}/receipt'
    #             image_url = lib.util.storage.upload_image(image_dir, image_name, image)
    #             order.meta["receipt_image"] = image_url
    #         except Exception as e:
    #             history = order.history
    #             history["receipt_image_error"] = str(e)

    #     order.meta["last_five_digit"] = last_five_digit
    #     order.meta['account_name'] = account_name
    #     order.meta['account_mode'] = account_mode
    #     order.payment_method = models.order.order.PAYMENT_METHOD_DIRECT
    #     order.status = "complete"
    #     order.save()

    #     lib.helper.order_helper.OrderHelper.sold_campaign_product(order.id)
    #     # content = lib.helper.order_helper.OrderHelper.get_confirmation_email_content(order)
    #     subject = lib.i18n.email.order_comfirm_mail.i18n_get_mail_subject(order, lang=campaign.lang)
    #     content = lib.i18n.email.order_comfirm_mail.i18n_get_mail_content(order, campaign, lang=campaign.lang)
    #     jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)     #queue this to redis if needed

    #     return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)


    # @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<order_oid>[^/.]+)/state', permission_classes=())
    # @lib.error_handle.error_handler.api_error_handler.api_error_handler
    # def check_guest_order_state(self, request, order_oid):

    #     order = lib.util.verify.Verify.get_order_with_oid(order_oid)
    #     return Response(order.status, status=status.HTTP_200_OK)


    # ----------------------------------------------- buyer ----------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/(?P<order_oid>[^/.]+)/platform', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_order_platform(self, request, order_oid):
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        return Response(order.platform, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/(?P<order_oid>[^/.]+)/subscription', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_order_with_user_subscription(self, request, order_oid):
        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        data = models.order.order_product.OrderWithUserSubscriptionWithOrderProductSerializer(order).data
        # from pprint import pprint
        # pprint(dict(data))
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/(?P<order_oid>[^/.]+)', permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_order(self, request, order_oid):

        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        return Response(models.order.order_product.OrderWithOrderProductSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/latest/shipping', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_latest_order_shipping(self, request):
        api_user = lib.util.verify.Verify.get_customer_user(request)
        order = api_user.orders.last()
        print(order.id)
        data = models.order.order.OrderSerializerUpdateShipping(order).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<order_oid>[^/.]+)/buyer/receipt/upload', parser_classes=(MultiPartParser,), permission_classes=())
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_upload_receipt(self, request, order_oid):


        order = lib.util.verify.Verify.get_order_with_oid(order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_order(order)
        last_five_digit, image, account_name, account_mode = lib.util.getter.getdata(request,('last_five_digit', 'image', 'account_name', 'account_mode'), required=False)

        if image not in [None, '', "undefined", 'null']:
            try:
                image_name = image.name.replace(" ","")
                image_dir = f'campaign/{order.campaign.id}/order/{order.id}/receipt'
                image_url = lib.util.storage.upload_image(image_dir, image_name, image)
                order.meta["receipt_image"] = image_url
            except Exception as e:
                history = order.history
                history["receipt_image_error"] = str(e)
                
        order.meta["last_five_digit"] = last_five_digit
        order.meta['account_name'] = account_name
        order.meta['account_mode'] = account_mode
        order.payment_method = models.order.order.PAYMENT_METHOD_DIRECT
        order.status = models.order.order.STATUS_COMPLETE
        order.save()

        for campaign_product_id_str, qty in order.products.items():
            pymongo_campaign_product = database.lss.campaign_product.CampaignProduct(id=int(campaign_product_id_str))
            pymongo_campaign_product.sold(qty, sync=True)
            lib.helper.cart_helper.CartHelper.send_campaign_product_websocket_data(pymongo_campaign_product.data)
        subject = lib.i18n.email.order_comfirm_mail.i18n_get_mail_subject(order, lang=campaign.lang)
        content = lib.i18n.email.order_comfirm_mail.i18n_get_mail_content(order, campaign, lang=campaign.lang)

        jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)     #queue this to redis if needed

        return Response(models.order.order_product.OrderWithOrderProductSerializer(order).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'buyer/history', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_buyer_order_history(self, request):

        api_user = lib.util.verify.Verify.get_customer_user(request)

        page = self.paginate_queryset(api_user.orders.all().order_by('-created_at'))
        if page is not None:
            serializer = models.order.order.OrderWithCampaignSerializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            data = models.order.order_product.OrderWithOrderProductSerializer(api_user.orders, many=True).data

        return Response(data, status=status.HTTP_200_OK)
       

    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/(?P<order_oid>[^/.]+)/state', permission_classes=())
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
        serializer = models.order.order_product.OrderWithOrderProductSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['GET'], url_path=r'seller/retrieve/oid', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_retrieve_order_oid(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        order = lib.util.verify.Verify.get_order(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, order.campaign.id)
        oid = database.lss.order.get_oid_by_id(order.id)

        return Response(oid, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'seller/search', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_merge_order_list(self, request):

        api_user, campaign_id, search, page, page_size, order_status, = lib.util.getter.getparams(request, ( 'campaign_id', 'search', 'page', 'page_size','status'),with_user=True, seller=True)
        
        payment_dict, delivery_dict, platform_dict, sort_by_dict = lib.util.getter.getdata(request,('payment','delivery','platform', 'sort_by'), required=False)

        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)
        queryset = campaign.orders.all()

        if search not in ["",None,'undefined'] and search.isnumeric():
            queryset=queryset.filter(Q(id=int(search))|Q(customer_name__contains=search))
        elif search not in ["",None,'undefined']:
            queryset=queryset.filter(customer_name__contains=search)

        elif order_status in models.order.order.STATUS_CHOICES:
            queryset=queryset.filter(status=order_status)

        if payment_dict:
            queryset=queryset.filter(payment_method__in=[key for key,value in payment_dict.items() if value])
        if delivery_dict:
            queryset=queryset.filter(delivery_status__in=[key for key,value in delivery_dict.items() if value])
        if platform_dict:
            queryset=queryset.filter(platform__in=[key for key,value in platform_dict.items() if value])

        for order_by, asc in sort_by_dict.items():
            if order_by not in ["id","subtotal","total",'payment_method', 'status']:
                continue
            order_by = order_by if asc==1 else f"-{order_by}"
            queryset = queryset.order_by(order_by)

        page = self.paginate_queryset(queryset)
        serializer = models.order.order.OrderSerializer(page, many=True)
        result = self.get_paginated_response(serializer.data)
        data = result.data

        return Response(data, status=status.HTTP_200_OK)

        # json_data, total_count = database.lss.campaign.get_merge_order_list_pagination(campaign.id, search, order_status, payment_list, delivery_list, platform_list , int(page), int(page_size), sort_by)

        # return Response({'count':total_count,'data':json_data}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PUT'], url_path=r'seller/deliver', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_deliver_order(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        order = lib.util.verify.Verify.get_order(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, order.campaign.id)
        
        subject = lib.i18n.email.delivery_comfirm_mail.i18n_get_mail_subject(order=order, lang=order.campaign.lang) 
        content = lib.i18n.email.delivery_comfirm_mail.i18n_get_mail_content(order=order, user=api_user, lang=order.campaign.lang) 
        jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)
        order.status = models.order.order.STATUS_SHIPPED
        order.save()

        return Response(models.order.order_product.OrderWithOrderProductSerializer(order).data, status=status.HTTP_200_OK)
    
    