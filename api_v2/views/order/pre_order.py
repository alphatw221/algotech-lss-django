from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from api import models
from django.db.models import Q
from api.models import campaign
from api.utils.common.order_helper import PreOrderHelper
from api.utils.common.verify import ApiVerifyError
import lib
import datetime


class PreOrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PreOrderViewSet(viewsets.ModelViewSet):
    queryset = models.order.pre_order.PreOrder.objects.all().order_by('id')
    serializer_class = models.order.pre_order.PreOrderSerializer
    filterset_fields = []
    pagination_class = PreOrderPagination


# ---------------------------------------------- buyer ------------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'(?P<campaign_id>[^/.]+)/(?P<login_with>[^/.]+)/buyer/create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_create_pre_order(self, request, campaign_id, login_with):

        api_user = lib.util.verify.Verify.get_customer_user(request)

        customer_id= getattr(api_user,f'{login_with}_info',{}).get('id')    #Facebook App Scope ID Here
        customer_name= getattr(api_user,f'{login_with}_info',{}).get('name')
        customer_img= getattr(api_user,f'{login_with}_info',{}).get('picture')

        if not customer_id or not customer_name :
            raise lib.error_handle.error.api_error.ApiVerifyError('Invalid User')

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

        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_pre_order(self, request, pk=None):

        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, campaign, save=True)

        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)
      
    
    @action(detail=True, methods=['GET'], url_path=r'buyer/retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_pre_order(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        pre_order = lib.util.verify.Verify.get_pre_order(pk)

        if pre_order.buyer and pre_order.buyer != api_user:
            raise lib.error_handle.error.api_error.ApiVerifyError('Invalid User')

        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, campaign, save=True)

        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'delivery', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_delivery_info(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_customer_user(request)
        
        shipping_data, = \
            lib.util.getter.getdata(request, ("shipping_data",), required=True)
        # shipping_option, = lib.util.getter.getdata(request, ("shipping_option",), required=False)
        print(shipping_data)
        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        campaign = lib.util.verify.Verify.get_campaign_from_pre_order(pre_order)

        serializer = models.order.pre_order.PreOrderSerializerUpdateDelivery(pre_order, data=shipping_data, partial=True) 
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pre_order = serializer.save()
        
        pre_order = lib.helper.order_helper.PreOrderHelper.summarize_pre_order(pre_order, campaign, save=True)

        #checkout

        api_order = PreOrderHelper.checkout(api_user, pre_order)
        order = lib.util.verify.Verify.get_order(api_order['id'])


        return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'buyer/add', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    @lib.error_handle.error_handler.order_operation_error_handler.order_operation_error_handler
    def buyer_add_order_product(self, request, pk=None):
        api_user, campaign_product_id, qty = lib.util.getter.getparams(request, ('campaign_product_id', 'qty',), with_user=True, seller=False)

        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        campaign_product = lib.util.verify.Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id)

        PreOrderHelper.add_product(api_user, pre_order, campaign_product, qty)
        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)

# ---------------------------------------------- seller ------------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'seller/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_list_pre_order(self, request):

        api_user, campaign_id, search = lib.util.getter.getparams(request, ('campaign_id', 'search'), with_user=True, seller=True)

        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        print (user_subscription.campaigns.filter(id='452'))
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
    
    @action(detail=True, methods=['PUT'], url_path=r'seller/adjust', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_adjust(self, request, pk=None):

        adjust_price, adjust_title, free_delivery = lib.util.getter.getdata(request, ('adjust_price', 'adjust_title', 'free_delivery'))
        adjust_price = float(adjust_price)
        api_user = lib.util.verify.Verify.get_seller_user(request)
        pre_order = lib.util.verify.Verify.get_pre_order(pk)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, pre_order.campaign.id)
        if type(free_delivery) != bool:
            raise ApiVerifyError("request data error")

        original_total = pre_order.total
        original_free_delivery = pre_order.free_delivery

        if pre_order.subtotal + adjust_price < 0:
            adjust_price = -pre_order.subtotal

        pre_order.adjust_price = adjust_price
        pre_order.free_delivery = free_delivery
        pre_order.adjust_title = adjust_title

        if free_delivery:
            pre_order.total = pre_order.subtotal + pre_order.adjust_price
        else:
            pre_order.total = pre_order.subtotal + pre_order.adjust_price + pre_order.shipping_cost

        seller_adjust_history = pre_order.history.get('seller_adjust', [])
        seller_adjust_history.append(
            {"original_total": original_total,
             "adjusted_total": pre_order.total,
             "original_free_delivery_status": original_free_delivery,
             "adjusted_free_delivery_status": pre_order.free_delivery,
             "adjusted_at": datetime.datetime.utcnow(),
             "adjusted_by": api_user.id
             }
        )
        pre_order.history['seller_adjust_history'] = seller_adjust_history

        pre_order.save()
        return Response(models.order.pre_order.PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)
    
    