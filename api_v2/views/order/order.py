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
import factory



from automation import jobs
from api.utils.error_handle.error_handler.email_error_handler import email_error_handler


class OrderSerializerWithCampaign(models.order.order.OrderSerializer):
    campaign = models.campaign.campaign.CampaignSerializer(read_only=True, default=dict)

class OrderSerializerWithOrderProduct(models.order.order.OrderSerializer):
    order_products = models.order.order_product.OrderProductSerializer(many=True, read_only=True, default=list)
    
class OrderSerializerWithOrderProductWithCampaign(OrderSerializerWithOrderProduct):
    campaign = models.campaign.campaign.CampaignSerializer(read_only=True, default=dict)


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
        return Response(OrderSerializerWithOrderProductWithCampaign(order).data, status=status.HTTP_200_OK)

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
        order.payment_status = models.order.order.PAYMENT_STATUS_AWAITING_CONFIRM
        lib.helper.order_helper.OrderStatusHelper.update_order_status(order, save=True)


        for campaign_product_id_str, qty in order.products.items():
            pymongo_campaign_product = database.lss.campaign_product.CampaignProduct(id=int(campaign_product_id_str))
            pymongo_campaign_product.sold(qty, sync=True)
            lib.helper.cart_helper.CartHelper.send_campaign_product_websocket_data(pymongo_campaign_product.data)
        subject = lib.i18n.email.order_comfirm_mail.i18n_get_mail_subject(order, lang=campaign.lang)
        content = lib.i18n.email.order_comfirm_mail.i18n_get_mail_content(order, campaign, lang=campaign.lang)

        jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)     #queue this to redis if needed

        return Response(OrderSerializerWithOrderProductWithCampaign(order).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'buyer/history', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_buyer_order_history(self, request):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        user_subscription_id, points_relative = lib.util.getter.getparams(request, ('user_subscription_id', 'points_relative'), with_user=False)

        queryset = api_user.orders.all()
        if user_subscription_id not in ["", None,'undefined','null'] and user_subscription_id.isnumeric():
            queryset=queryset.filter(user_subscription_id = int(user_subscription_id))

        if points_relative:
            queryset=queryset.filter(Q(points_earned__gt = 0)|Q(points_used__gt = 0)|Q(point_discount__gt = 0))
 

        queryset = queryset.order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = OrderSerializerWithCampaign(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            
            data = OrderSerializerWithCampaign(api_user.orders, many=True).data

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
        serializer = OrderSerializerWithOrderProductWithCampaign(order)

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
        
        payment_methods_dict, delivery_status_options_dict, payment_status_options_dict,  platform_dict, sort_by_dict = \
            lib.util.getter.getdata(request, ('payment_method_options','delivery_status_options', 'payment_status_options', 'platform_options', 'sort_by'), required=False)

        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        # campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)
        queryset = user_subscription.orders.all()

        if campaign_id not in ["",None,'undefined'] and campaign_id.isnumeric():
            queryset=queryset.filter(campaign_id = int(campaign_id))

        if search not in ["",None,'undefined'] and search.isnumeric():
            queryset=queryset.filter(Q(id=int(search))|Q(customer_name__contains=search))
        elif search not in ["",None,'undefined']:
            queryset=queryset.filter(customer_name__contains=search)

        elif order_status in models.order.order.STATUS_CHOICES:
            queryset=queryset.filter(status=order_status)

        if payment_methods_dict and[key for key,value in payment_methods_dict.items() if value]:
            queryset=queryset.filter(payment_method__in=[key for key,value in payment_methods_dict.items() if value])
        if delivery_status_options_dict and [key for key,value in delivery_status_options_dict.items() if value]:
            queryset=queryset.filter(delivery_status__in=[key for key,value in delivery_status_options_dict.items() if value])
        if payment_status_options_dict and [key for key,value in payment_status_options_dict.items() if value]:
            queryset=queryset.filter(payment_status__in=[key for key,value in payment_status_options_dict.items() if value])
        if platform_dict and [key for key,value in platform_dict.items() if value]:
            queryset=queryset.filter(platform__in=[key for key,value in platform_dict.items() if value])
        
        queryset = queryset.order_by('-created_at')
        
        for order_by, asc in sort_by_dict.items():
            if order_by not in ["id","subtotal","total",'payment_method', 'status']:
                continue
            order_by = order_by if asc==1 else f"-{order_by}"
            queryset = queryset.order_by(order_by)

        page = self.paginate_queryset(queryset)
        serializer = OrderSerializerWithCampaign(page, many=True)
        result = self.get_paginated_response(serializer.data)
        data = result.data

        return Response(data, status=status.HTTP_200_OK)

        # json_data, total_count = database.lss.campaign.get_merge_order_list_pagination(campaign.id, search, order_status, payment_list, delivery_list, platform_list , int(page), int(page_size), sort_by)

        # return Response({'count':total_count,'data':json_data}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PUT'], url_path=r'seller/delivery', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_update_delivery_status(self, request, pk=None):

        delivery_status, = lib.util.getter.getdata(request, ('delivery_status',), required=True)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        order = lib.util.verify.Verify.get_order(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, order.campaign.id)
        
        if delivery_status not in models.order.order.DELIVERY_STATUS_CHOICES:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid')

        order.delivery_status = delivery_status
        lib.helper.order_helper.OrderStatusHelper.update_order_status(order, save=True)

        # subject = lib.i18n.email.delivery_comfirm_mail.i18n_get_mail_subject(order=order, lang=order.campaign.lang) 
        # content = lib.i18n.email.delivery_comfirm_mail.i18n_get_mail_content(order=order, user=api_user, lang=order.campaign.lang) 
        # jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)
        
        return Response(OrderSerializerWithOrderProductWithCampaign(order).data, status=status.HTTP_200_OK)
    
    
    @action(detail=True, methods=['PUT'], url_path=r'seller/payment', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_update_payment_status(self, request, pk=None):

        payment_status, = lib.util.getter.getdata(request, ('payment_status',), required=True)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        order = lib.util.verify.Verify.get_order(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, order.campaign.id)
        
        if payment_status not in models.order.order.PAYMENT_STATUS_CHOICES:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid')

        if payment_status == models.order.order.PAYMENT_STATUS_PAID and order.payment_status != models.order.order.PAYMENT_STATUS_PAID:

            point_discount_processor_class:lib.helper.discount_helper.PointDiscountProcessor = lib.helper.discount_helper.get_point_discount_processor_class(order.campaign.user_subscription)
            point_discount_processor = point_discount_processor_class(order.buyer, order.campaign.user_subscription, None, order.campaign.meta_point, points_earned = order.points_earned)
            point_discount_processor.update_wallet()

        order.payment_status = payment_status
        order.save()
        # lib.helper.order_helper.OrderStatusHelper.update_order_status(order, save=True)

        # subject = lib.i18n.email.delivery_comfirm_mail.i18n_get_mail_subject(order=order, lang=order.campaign.lang) 
        # content = lib.i18n.email.delivery_comfirm_mail.i18n_get_mail_content(order=order, user=api_user, lang=order.campaign.lang) 
        # jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)
        
        return Response(OrderSerializerWithOrderProductWithCampaign(order).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'report', permission_classes=(IsAuthenticated, ))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def get_order_report(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        order_export_processor_class:factory.order_export.OrderExportProcessor = factory.order_export.get_order_export_processor_class(user_subscription)
        order_export_processor = order_export_processor_class(user_subscription, **request.query_params)
        
        order_data = order_export_processor.export_order_data()
        return Response(order_data, status=status.HTTP_200_OK)
