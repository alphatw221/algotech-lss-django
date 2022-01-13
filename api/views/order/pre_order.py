from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from api.models.order.pre_order import PreOrder, PreOrderSerializer, PreOrderSerializerUpdatePaymentShipping
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError, platform_dict
from api.utils.common.common import *
from api.utils.common.order_helper import PreOrderHelper
from backend.pymongo.mongodb import db

from django.db.models import Q
def verify_buyer_request(api_user, platform_name, campaign_id, order_product_id=None, campaign_product_id=None, check_info=None):
    
    if platform_name not in platform_dict:
        raise ApiVerifyError("no platfrom name found")
    
    if platform_name=='facebook':
        customer_id=api_user.facebook_info['id']
    else:
        raise ApiVerifyError('platform not support')

    if not PreOrder.objects.filter(platform=platform_name, customer_id=customer_id, campaign_id=campaign_id).exists():
        print ('customer_id')
        print (customer_id)
        raise ApiVerifyError('no pre_order found')
    pre_order =PreOrder.objects.get(platform=platform_name, customer_id=customer_id, campaign_id=campaign_id)
    
    if order_product_id:
        if not pre_order.order_products.filter(id=order_product_id).exists():
            raise ApiVerifyError("no order_product found")
        order_product = pre_order.order_products.get(
            id=order_product_id)
        campaign_product = order_product.campaign_product

        return pre_order, campaign_product, order_product

    if campaign_product_id:
        if not pre_order.campaign.products.filter(id=campaign_product_id).exists():
            raise ApiVerifyError("no campaign_product found")
        campaign_product = pre_order.campaign.products.get(
            id=campaign_product_id)
        if campaign_product.type=='lucky_draw' or campaign_product.type=='lucky_draw-fast':
            raise ApiVerifyError("invalid campaign_product")
        return pre_order, campaign_product

    if check_info == None:
        return pre_order

    verify_message = {}
    check_exist = False
    #TODO 訊息彙整回傳一次
    if not pre_order.shipping_first_name:
        check_exist = True
        verify_message['shipping_first_name'] = 'not valid'
    if not pre_order.shipping_last_name:
        check_exist = True
        verify_message['shipping_last_name'] = 'not valid'
    if not pre_order.shipping_phone:
        check_exist = True
        verify_message['shipping_phone'] = 'not valid'
    if not pre_order.shipping_postcode:
        check_exist = True
        verify_message['shipping_postcode'] = 'not valid'
    if not pre_order.shipping_region:
        check_exist = True
        verify_message['shipping_region'] = 'not valid'
    if not pre_order.shipping_location:
        check_exist = True
        verify_message['shipping_location'] = 'not valid'
    if not pre_order.shipping_address_1:
        check_exist = True
        verify_message['shipping_address'] = 'not valid'
    if not pre_order.shipping_method:
        check_exist = True
        verify_message['shipping_method'] = 'not valid'
    if not pre_order.payment_first_name:
        check_exist = True
        verify_message['payment_first_name'] = 'not valid'
    if not pre_order.payment_last_name:
        check_exist = True
        verify_message['payment_last_name'] = 'not valid'
    if not pre_order.payment_company:
        check_exist = True
        verify_message['payment_company'] = 'not valid'
    if not pre_order.payment_postcode:
        check_exist = True
        verify_message['payment_postcode'] = 'not valid'
    if not pre_order.payment_region:
        check_exist = True
        verify_message['payment_region'] = 'not valid'
    if not pre_order.payment_location:
        check_exist = True
        verify_message['payment_location'] = 'not valid'
    if not pre_order.payment_address_1:
        check_exist = True
        verify_message['payment_address'] = 'not valid'
    if check_exist == True:
        raise ApiVerifyError(verify_message)
    return pre_order

def verify_seller_request(api_user, platform_name, platform_id, campaign_id, pre_order_id=None, order_product_id=None, campaign_product_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign(platform, campaign_id)

    if pre_order_id:
        if not campaign.pre_orders.filter(id=pre_order_id).exists():
            raise ApiVerifyError('no pre_order found')
        pre_order = campaign.pre_orders.get(id=pre_order_id)

        if order_product_id:
            if not pre_order.order_products.filter(id=order_product_id).exists():
                raise ApiVerifyError("no order_product found")
            order_product = pre_order.order_products.get(
                id=order_product_id)
            campaign_product = order_product.campaign_product
            return platform, campaign, pre_order, campaign_product, order_product

        if campaign_product_id:
            if not pre_order.campaign.products.filter(id=campaign_product_id).exists():
                raise ApiVerifyError("no campaign_product found")
            campaign_product = pre_order.campaign.products.get(
                id=campaign_product_id)
            return platform, campaign, pre_order, campaign_product

        return platform, campaign, pre_order

    return platform, campaign


class PreOrderPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class PreOrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = PreOrder.objects.all().order_by('id')
    serializer_class = PreOrderSerializer
    filterset_fields = []
    pagination_class = PreOrderPagination

    @action(detail=True, methods=['GET'], url_path=r'seller_retrieve')
    @api_error_handler
    def seller_retrieve_pre_order(self, request, pk=None):
        api_user, platform_id, platform_name, campaign_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id"))

        _, _, pre_order = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

        serializer = PreOrderSerializer(pre_order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller_list')
    @api_error_handler
    def seller_list_pre_order(self, request):
        api_user, platform_id, platform_name, campaign_id, search = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "search"))

        _, campaign = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id)

        queryset = campaign.pre_orders.all()

        if search:
            if search.isnumeric():
                queryset = queryset.filter(Q(id=int(search)) | Q(customer_name__icontains=search) | Q(phone__icontains=search))
            else:
                queryset = queryset.filter(Q(customer_name__icontains=search) | Q(phone__icontains=search))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PreOrderSerializer(page, many=True)
            result = self.get_paginated_response(
                serializer.data)
            data = result.data
        else:
            serializer = PreOrderSerializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

        # if queryset.exists():
        #     page = self.paginate_queryset(queryset)
        #     if page is not None:
        #         serialized = VideoSerializer(page, many=True)
        #         return self.get_paginated_response(serialized.data)
        # return Response(status=http_status.HTTP_404_NOT_FOUND)


    @action(detail=True, methods=['GET'], url_path=r'seller_checkout')
    @api_error_handler
    def seller_pre_order_checkout(self, request, pk=None):

        api_user, platform_id, platform_name, campaign_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id"))

        _, _, pre_order = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk)

        api_order = PreOrderHelper.checkout(api_user, pre_order)
        return Response(api_order, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_add')
    @api_error_handler
    def seller_add_order_product(self, request, pk=None):
        api_user, platform_id, platform_name, campaign_id, campaign_product_id, qty = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "campaign_product_id", "qty"))

        _, _, pre_order, campaign_product = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk, campaign_product_id=campaign_product_id)

        api_order_product = PreOrderHelper.add_product(
            api_user, pre_order, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_update')
    @api_error_handler
    def seller_update_order_product(self, request, pk=None):

        api_user, platform_id, platform_name, campaign_id, order_product_id, qty = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "order_product_id", "qty"))

        _, _, pre_order, campaign_product, order_product = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk, order_product_id=order_product_id)

        api_order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_delete')
    @api_error_handler
    def seller_delete_order_product(self, request, pk=None):

        api_user, platform_id, platform_name, campaign_id, order_product_id = getparams(
            request, ("platform_id", "platform_name", "campaign_id", "order_product_id"))

        _, _, pre_order, campaign_product, order_product = verify_seller_request(
            api_user, platform_name, platform_id, campaign_id, pre_order_id=pk, order_product_id=order_product_id)

        PreOrderHelper.delete_product(
            api_user, pre_order, order_product, campaign_product)
        return Response({'message':"delete success"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], url_path=r'delivery_info')
    @api_error_handler
    def update_buyer_submit(self, request, pk=None):
        api_user, platform_name, campaign_id = getparams(
            request, ("platform_name", "campaign_id"), seller=False)
        pre_order = verify_buyer_request(
            api_user, platform_name, campaign_id)
        
        # request.data['status'] = 'unpaid'
        serializer = PreOrderSerializerUpdatePaymentShipping(pre_order, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        pre_order = verify_buyer_request(
            api_user, platform_name, campaign_id, check_info=True)
        serializer = PreOrderSerializer(pre_order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_retrieve')
    @api_error_handler
    def buyer_retrieve_pre_order(self, request):
        api_user, platform_name, campaign_id = getparams(
            request, ("platform_name", "campaign_id"), seller=False)

        pre_order = verify_buyer_request(
            api_user, platform_name, campaign_id)

        serializer = PreOrderSerializer(pre_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_checkout')
    @api_error_handler
    def buyer_pre_order_checkout(self, request):

        api_user, platform_name, campaign_id = getparams(
            request, ("platform_name", "campaign_id"), seller=False)
            
        pre_order = verify_buyer_request(
            api_user, platform_name, campaign_id)
        api_order = PreOrderHelper.checkout(api_user, pre_order)
        return Response(api_order, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_add')
    @api_error_handler
    def buyer_add_order_product(self, request):
        api_user, platform_name, campaign_id, campaign_product_id, qty = getparams(
            request, ("platform_name", "campaign_id", "campaign_product_id", "qty"), seller=False)

        pre_order, campaign_product = verify_buyer_request(
            api_user, platform_name, campaign_id, campaign_product_id=campaign_product_id)

        api_order_product = PreOrderHelper.add_product(api_user, pre_order, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_update')
    @api_error_handler
    def buyer_update_order_product(self, request):
        api_user, platform_name, campaign_id, order_product_id, qty = getparams(
            request, ("platform_name", "campaign_id", "order_product_id", "qty"), seller=False)

        pre_order, campaign_product, order_product = verify_buyer_request(
            api_user, platform_name, campaign_id, order_product_id=order_product_id)

        api_order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'buyer_delete')
    @api_error_handler
    def buyer_delete_order_product(self, request):
        api_user, platform_name, campaign_id, order_product_id= getparams(
            request, ("platform_name", "campaign_id", "order_product_id"), seller=False)

        pre_order, campaign_product, order_product = verify_buyer_request(
            api_user, platform_name, campaign_id, order_product_id=order_product_id)

        PreOrderHelper.delete_product(
            api_user, pre_order, order_product, campaign_product)
        return Response({'message':"delete success"}, status=status.HTTP_200_OK)