from calendar import c
from django.http import JsonResponse
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


from api import models

from automation import jobs

import lib

import uuid
import service
import database
import traceback
from datetime import datetime

class PreOrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PreOrderViewSet(viewsets.ModelViewSet):
    queryset = models.order.pre_order.PreOrder.objects.all().order_by('id')
    serializer_class = models.order.pre_order.PreOrderSerializer
    filterset_fields = []
    pagination_class = PreOrderPagination

# ---------------------------------------------- guest ------------------------------------------------------
    @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<pre_order_oid>[^/.]+)/platform', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_retrieve_pre_order_platform(self, request, pre_order_oid):
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        return Response(pre_order.platform, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'guest/retrieve/(?P<pre_order_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_retrieve_pre_order(self, request, pre_order_oid):
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)

        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, campaign, save=True)

        return Response(models.order.pre_order.PreOrderSerializerWithSubscription(pre_order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<pre_order_oid>[^/.]+)/guest/add', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def guest_add_order_product(self, request, pre_order_oid):

        campaign_product_id, qty = lib.util.getter.getparams(request, ('campaign_product_id', 'qty',), with_user=False)

        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id)

        lib.helper.order_helper.PreOrderHelper.add_product(None,pre_order.id, campaign_product.id, qty)
        pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<pre_order_oid>[^/.]+)/guest/delivery', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def guest_update_delivery_info(self, request, pre_order_oid):
        
        shipping_data, = \
            lib.util.getter.getdata(request, ("shipping_data",), required=True)
        # discount_code = \
        #     lib.util.getter.getdata(request, ("discount_code",), required=False)

        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)

        # discount = None
        # for _discount in campaign.discounts:
        #     if discount_code and discount_code == _discount.get('code'):
        #         discount = _discount
        #         break
        # if discount_code and not discount:
        #     raise lib.error_handle.error.api_error.ApiVerifyError('invalid_discount_code')

        serializer = models.order.pre_order.PreOrderSerializerUpdateDelivery(pre_order, data=shipping_data, partial=True) 
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pre_order = serializer.save()
        
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, campaign, save=True)

        #checkout

        success, api_order = lib.helper.order_helper.PreOrderHelper.checkout(None, campaign.id, pre_order.id)

        if not success:
            pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
            return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_205_RESET_CONTENT)

        order = lib.util.verify.Verify.get_order(api_order.id)

        subject = lib.helper.order_helper.OrderHelper.i18n_get_mail_subject(order,lang=campaign.lang)
        content = lib.helper.order_helper.OrderHelper.get_checkout_email_content(order,api_order._id,lang=campaign.lang)
        jobs.send_email_job.send_email_job(subject, order.shipping_email, content=content)     
        #queue this to redis if needed 
        data = models.order.order.OrderSerializer(order).data
        data['oid']=str(api_order._id)

        #send email to customer over here order detail link
        return Response(data, status=status.HTTP_200_OK)




    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/guest/create', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_create_pre_order(self, request, campaign_id):

        recaptcha_token, client_uuid = lib.util.getter.getparams(request, ('recaptcha_token', 'client_uuid'), with_user=False)
        
        code, response = service.recaptcha.recaptcha.verify_token(recaptcha_token)

        if code!=200 or not response.get('success'):
            raise lib.error_handle.error.api_error.ApiVerifyError('refresh_try_again')
        
        if not client_uuid or client_uuid in ['null', 'undefined']:
            client_uuid = str(uuid.uuid4())

        customer_id= client_uuid   #Facebook App Scope ID Here
        customer_name= ''

        campaign = lib.util.verify.Verify.get_campaign(campaign_id)

        if models.order.pre_order.PreOrder.objects.filter(customer_id = customer_id, campaign = campaign, platform = None,).exists():
            pre_order = models.order.pre_order.PreOrder.objects.get(customer_id = customer_id, campaign = campaign, platform = None,)
        else:
            
            pre_order = models.order.pre_order.PreOrder.objects.create(
                customer_id = customer_id,
                customer_name = customer_name,
                campaign = campaign,
                platform = None,
                platform_id = None)

            for campaign_product in campaign.products.filter(Q(type=models.campaign.campaign_product.TYPE_PRODUCT)|Q(type=models.campaign.campaign_product.TYPE_PRODUCT_FAST)):   #status=True cause databaseError here

                if not campaign_product.status or not campaign_product.qty_for_sale - campaign_product.qty_sold:
                    continue

                try:
                    lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order.id, campaign_product.id, 1)
                except Exception:
                    print('add_proudct fail')
                    print(traceback.format_exc())
                    continue
            
        pre_order_oid = database.lss.pre_order.get_oid_by_id(pre_order.id)
        
        response = JsonResponse({'client_uuid':client_uuid, 'pre_order_oid':pre_order_oid})
        response.set_cookie('client_uuid', client_uuid, path="/")

        return response

# ---------------------------------------------- buyer ------------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/(?P<login_with>[^/.]+)/buyer/create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_create_pre_order(self, request, campaign_id, login_with):

        api_user = lib.util.verify.Verify.get_customer_user(request)

        if login_with not in ['facebook','youtube','instagram']:
            customer_id = api_user.id
            customer_name= api_user.name
            customer_img= api_user.image
            platform = 'lss'
        else:
            customer_id= getattr(api_user,f'{login_with}_info',{}).get('id')    #Facebook App Scope ID Here
            customer_name= getattr(api_user,f'{login_with}_info',{}).get('name')
            customer_img= getattr(api_user,f'{login_with}_info',{}).get('picture')
            platform = login_with
            
        if not customer_id or not customer_name :
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_user')

        campaign = lib.util.verify.Verify.get_campaign(campaign_id)

        if models.order.pre_order.PreOrder.objects.filter(customer_id = customer_id, campaign = campaign, platform = None,).exists():
            pre_order = models.order.pre_order.PreOrder.objects.get(customer_id = customer_id, campaign = campaign, platform = None,)
        else:
            pre_order = models.order.pre_order.PreOrder.objects.create(
                customer_id = customer_id,
                customer_name = customer_name,
                customer_img = customer_img,
                campaign = campaign,
                buyer = api_user,
                platform = None,
                platform_id = None)

            for campaign_product in campaign.products.filter(Q(type=models.campaign.campaign_product.TYPE_PRODUCT)|Q(type=models.campaign.campaign_product.TYPE_PRODUCT_FAST)):   #status=True cause databaseError here

                if not campaign_product.status or not campaign_product.qty_for_sale - campaign_product.qty_sold:
                    continue

                try:
                    lib.helper.order_helper.PreOrderHelper.add_product(None, pre_order.id, campaign_product.id, 1)
                except Exception:
                    print('add_proudct fail')
                    print(traceback.format_exc())
                    continue

        pre_order_oid = database.lss.pre_order.get_oid_by_id(pre_order.id)
        return Response({ 'pre_order_oid':pre_order_oid}, status=status.HTTP_200_OK)


    
    @action(detail=False, methods=['GET'], url_path=r'buyer/retrieve/(?P<pre_order_oid>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_retrieve_pre_order(self, request, pre_order_oid):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)

        if pre_order.buyer and pre_order.buyer != api_user:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_user')

        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, campaign, save=True)

        return Response(models.order.pre_order.PreOrderSerializerWithSubscription(pre_order).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<pre_order_oid>[^/.]+)/buyer/delivery', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def buyer_update_delivery_info(self, request, pre_order_oid):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        
        shipping_data, = \
            lib.util.getter.getdata(request, ("shipping_data",), required=True)
        # discount_code = \
        #     lib.util.getter.getdata(request, ("discount_code",), required=False)

        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)

        # discount = None
        # for _discount in campaign.discounts:
        #     if discount_code and discount_code == _discount.get('code'):
        #         discount = _discount
        #         break
        # if discount_code and not discount:
        #     raise lib.error_handle.error.api_error.ApiVerifyError('invalid_discount_code')


        serializer = models.order.pre_order.PreOrderSerializerUpdateDelivery(pre_order, data=shipping_data, partial=True) 
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pre_order = serializer.save()
        
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, campaign, save=True)

        #checkout

        success, api_order = lib.helper.order_helper.PreOrderHelper.checkout(api_user, campaign.id, pre_order.id)

        if not success:
            pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
            return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_400_BAD_REQUEST)

        order = lib.util.verify.Verify.get_order(api_order.id)
        data = models.order.order.OrderSerializer(order).data
        data['oid']=str(api_order._id)
        
        # change buyer language
        api_user.lang = campaign.lang
        api_user.save()

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'], url_path=r'(?P<pre_order_oid>[^/.]+)/buyer/add', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def buyer_add_order_product(self, request, pre_order_oid):
        api_user, campaign_product_id, qty = lib.util.getter.getparams(request, ('campaign_product_id', 'qty',), with_user=True, seller=False)

        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id)

        lib.helper.order_helper.PreOrderHelper.add_product(api_user, pre_order.id, campaign_product.id, qty)
        pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['PUT'], url_path=r'(?P<pre_order_oid>[^/.]+)/buyer/discount',  permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_apply_discount_code(self, request, pre_order_oid):

        # api_user = lib.util.verify.Verify.get_customer_user(request)

        discount_code, = \
            lib.util.getter.getdata(request, ("discount_code",), required=True)

        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)

        discount_codes = campaign.user_subscription.discount_codes.filter(start_at__lte=datetime.utcnow()).filter(end_at__gte=datetime.utcnow())

        valid_discount_code = None
        for _discount_code in discount_codes:
            if discount_code == _discount_code.code:
                valid_discount_code = _discount_code
                break
        if not valid_discount_code:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_discount_code')
        
        for limitation in valid_discount_code.limitations:
            if not lib.helper.discount_helper.check_limitation(limitation, pre_order):
                 raise lib.error_handle.error.api_error.ApiVerifyError('not_eligible')
 

        discount_code_data = valid_discount_code.__dict__
        del discount_code_data['_state']
        pre_order.applied_discount = discount_code_data


        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, campaign, save=True)

        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)

# ---------------------------------------------- seller ------------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'seller/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_list_pre_order(self, request):

        api_user, campaign_id, search = lib.util.getter.getparams(request, ('campaign_id', 'search'), with_user=True, seller=True)

        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        queryset = campaign.pre_orders.exclude(subtotal=0).order_by('id')

        if search:
            if search.isnumeric():
                queryset = queryset.filter(
                    Q(id=int(search)) | Q(customer_name__icontains=search) | Q(phone__icontains=search))
            else:
                queryset = queryset.filter(Q(customer_name__icontains=search) | Q(phone__icontains=search))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = models.order.pre_order.PreOrderSerializer(page, many=True)
            result = self.get_paginated_response(
                serializer.data)
            data = result.data
        else:
            serializer = models.order.pre_order.PreOrderSerializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'seller/retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_retrieve_pre_order(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)

        serializer = models.order.pre_order.PreOrderSerializer(pre_order)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'seller/retrieve/oid', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_retrieve_pre_order_oid(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        lib.util.verify.Verify.get_campaign_from_user_subscription(api_user.user_subscription, pre_order.campaign.id)
        oid = database.lss.pre_order.get_oid_by_id(pre_order.id)

        return Response(oid, status=status.HTTP_200_OK)
    @action(detail=True, methods=['PUT'], url_path=r'seller/adjust', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_adjust(self, request, pk=None):

        adjust_price, adjust_title, free_delivery = lib.util.getter.getdata(request, ('adjust_price', 'adjust_title', 'free_delivery'))
        if type(free_delivery) != bool or type(adjust_price) not in [int, float]:
            raise lib.error_handle.error.api_error.ApiVerifyError("request_data_error")
        adjust_price = float(adjust_price)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)

        original_total = pre_order.total
        original_free_delivery = pre_order.free_delivery

        if free_delivery:
            pre_order.total = pre_order.subtotal - pre_order.discount 
        else:
            pre_order.total = pre_order.subtotal - pre_order.discount + pre_order.shipping_cost

        pre_order.free_delivery = free_delivery
        pre_order.adjust_title = adjust_title
        pre_order.adjust_price = -pre_order.total if pre_order.total + adjust_price < 0 else adjust_price
        pre_order.total+=pre_order.adjust_price


        seller_adjust_history = pre_order.history.get('seller_adjust', [])
        seller_adjust_history.append(
            {"original_total": original_total,
             "adjusted_total": pre_order.total,
             "original_free_delivery_status": original_free_delivery,
             "adjusted_free_delivery_status": pre_order.free_delivery,
             "adjusted_at": datetime.utcnow(),
             "adjusted_by": api_user.id
             }
        )
        pre_order.history['seller_adjust_history'] = seller_adjust_history

        pre_order.save()
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], url_path=r'(?P<pre_order_id>[^/.]+)/seller/add', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def seller_add_order_product(self, request, pre_order_id):
        api_user, campaign_product_id, qty = lib.util.getter.getparams(request, ('campaign_product_id', 'qty',), with_user=True, seller=True)

        pre_order = lib.util.verify.Verify.get_pre_order(pre_order_id)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id)

        lib.helper.order_helper.PreOrderHelper.add_product(api_user, pre_order.id, campaign_product.id, qty)
        pre_order = lib.util.verify.Verify.get_pre_order(pre_order.id)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)
        
