import re
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from api.models.campaign.campaign import Campaign
from api.models.order.order_product import OrderProduct

from api.models.order.pre_order import PreOrder, PreOrderSerializer, PreOrderSerializerUpdatePaymentShipping
from api.utils.common.common import getdata, getparams
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError, platform_dict

from api.utils.common.order_helper import PreOrderHelper
from backend.pymongo.mongodb import db

from django.db.models import Q
import datetime
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler

from django.conf import settings
import traceback
from api.utils.error_handle.error.pre_order_error import PreOrderErrors
from django.core.exceptions import ObjectDoesNotExist

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
        api_user, platform_id, platform_name = getparams(request, ('platform_id', 'platform_name'), seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        pre_order=Verify.get_pre_order(pk)
        Verify.get_campaign_from_platform(platform, pre_order.campaign.id)
        serializer = PreOrderSerializer(pre_order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller_list')
    @api_error_handler
    def seller_list_pre_order(self, request):

        api_user, platform_id, platform_name, campaign_id, search = getparams(request, ('platform_id', 'platform_name', 'campaign_id', 'search'), seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        campaign = Verify.get_campaign_from_platform(platform, campaign_id)
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



    @action(detail=True, methods=['GET'], url_path=r'seller_checkout')
    @api_error_handler
    def seller_pre_order_checkout(self, request, pk=None):

        api_user, platform_id, platform_name = getparams(request, ('platform_id', 'platform_name'), seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        pre_order = Verify.get_pre_order(pk)
        Verify.get_campaign_from_platform(platform, pre_order.campaign.id)
        api_order = PreOrderHelper.checkout(api_user, pre_order)
        return Response(api_order, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_add')
    @api_error_handler
    def seller_add_order_product(self, request, pk=None):
        api_user, platform_id, platform_name, campaign_product_id, qty = getparams(request, ('platform_id', 'platform_name', 'campaign_product_id', 'qty'), seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        pre_order = Verify.get_pre_order(pk)
        Verify.get_campaign_from_platform(platform, pre_order.campaign.id)

        campaign_product = Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id)
        api_order_product = PreOrderHelper.add_product(
            api_user, pre_order, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_update')
    @api_error_handler
    def seller_update_order_product(self, request, pk=None):
        api_user, platform_id, platform_name, order_product_id, qty = getparams(request, ('platform_id', 'platform_name', 'order_product_id', 'qty'), seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        pre_order = Verify.get_pre_order(pk)
        Verify.get_campaign_from_platform(platform, pre_order.campaign.id)

        order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)
        api_order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, order_product.campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'seller_adjust')
    @api_error_handler
    def seller_adjust(self, request, pk=None):
        api_user, platform_id, platform_name = getparams(request, ('platform_id', 'platform_name'), with_user=True ,seller=True)

        adjust_price, adjust_title, free_delivery = getdata(request,('adjust_price', 'adjust_title', 'free_delivery'))


        platform = Verify.get_platform(api_user, platform_name, platform_id)
        pre_order = Verify.get_pre_order(pk)
        Verify.get_campaign_from_platform(platform, pre_order.campaign.id)

        if type(adjust_price) not in [int, float] or type(free_delivery) != bool:
            raise ApiVerifyError("request data error")

        last_adjust = pre_order.adjust_price if pre_order.adjust_price else 0

        adjust_difference = adjust_price - last_adjust


        adjust_price_history = pre_order.history.get('adjust_price',[])

        if pre_order.subtotal+adjust_difference < 0:
            adjust_difference = -pre_order.subtotal
        adjust_price_history.append({"original_subtotal":pre_order.subtotal, "adjusted_amount":adjust_difference, "adjusted_subtotal": pre_order.subtotal+adjust_difference, "adjusted_at":datetime.datetime.utcnow(), "adjusted_by":api_user.id})
        pre_order.history['adjust_price']=adjust_price_history
        pre_order.subtotal = pre_order.subtotal+adjust_difference
        pre_order.adjust_price = adjust_price
        pre_order.adjust_title = adjust_title

        if free_delivery:
            free_delievery_history = pre_order.history.get('free_delievery',[])
            free_delievery_history.append({"original_total":pre_order.total, "adjusted_total": pre_order.subtotal, "adjusted_at":datetime.datetime.utcnow(), "adjusted_by":api_user.id})
            pre_order.history['free_delievery']=free_delievery_history
            pre_order.total = pre_order.subtotal
            
        else:
            free_delievery_history = pre_order.history.get('free_delievery',[])
            free_delievery_history.append({"original_total":pre_order.total, "adjusted_total": pre_order.subtotal+pre_order.shipping_cost, "adjusted_at":datetime.datetime.utcnow(), "adjusted_by":api_user.id})
            pre_order.history['free_delievery']=free_delievery_history
            shipping_cost = pre_order.shipping_cost if pre_order.shipping_cost else 0
            pre_order.total = pre_order.subtotal+shipping_cost

        pre_order.free_delivery = free_delivery
        pre_order.save()
        
        return Response(PreOrderSerializer(pre_order).data, status=status.HTTP_200_OK)
    @action(detail=True, methods=['GET'], url_path=r'seller_delete')
    @api_error_handler
    def seller_delete_order_product(self, request, pk=None):
        api_user, platform_id, platform_name, order_product_id = getparams(request, ('platform_id', 'platform_name', 'order_product_id'), seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        pre_order = Verify.get_pre_order(pk)
        Verify.get_campaign_from_platform(platform, pre_order.campaign.id)

        order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)
        # api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search = Verify.PreOrderApi.FromSeller.verify(request, pk)
        PreOrderHelper.delete_product(
            api_user, pre_order, order_product, order_product.campaign_product)
        return Response({'message':"delete success"}, status=status.HTTP_200_OK)
    
    #------------------buyer---------------------------------------------------------------------------
    
    #TODO transfer to campaign or payment 
    @action(detail=True, methods=['GET'], url_path=r'campaign_info')
    @api_error_handler
    def get_campaign_info(self, request, pk=None):

        # OPERATION_CODE_NAME: AGILE
        if request.user.id in settings.ADMIN_LIST:
            pre_order=PreOrder.objects.get(id=pk)
            campaign = db.api_campaign.find_one({'id': pre_order.campaign_id})
            data_dict = {
                'campaign_id': pre_order.campaign_id,
                'platform': pre_order.platform,
                'platform_id': pre_order.platform_id,
                'meta_logistic': campaign['meta_logistic']
            }

            return Response(data_dict, status=status.HTTP_200_OK)

        api_user, pre_order, order_product, campaign_product, qty = Verify.PreOrderApi.FromBuyer.verify(request, pk)
        campaign = db.api_campaign.find_one({'id': pre_order.campaign_id})
        data_dict = {
            'campaign_id': pre_order.campaign_id,
            'platform': pre_order.platform,
            'platform_id': pre_order.platform_id,
            'meta_logistic': campaign['meta_logistic']
        }

        return Response(data_dict, status=status.HTTP_200_OK)

    #TODO transfer to campaign or payment 
    @action(detail=True, methods=['POST'], url_path=r'delivery_info')
    @api_error_handler
    def update_buyer_submit(self, request, pk=None):
        date_list = request.data['shipping_date'].split('-')
        request.data['shipping_date'] = datetime.date(int(date_list[0]), int(date_list[1]), int(date_list[2]))

        # OPERATION_CODE_NAME: AGILE
        if request.user.id in settings.ADMIN_LIST:
            pre_order=PreOrder.objects.get(id=pk)
            serializer = PreOrderSerializerUpdatePaymentShipping(pre_order, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            pre_order = PreOrder.objects.get(id=pk)
            verify_message = Verify.PreOrderApi.FromBuyer.verify_delivery_info(pre_order)
            return Response(verify_message, status=status.HTTP_200_OK)

        api_user, pre_order, order_product, campaign_product, qty = Verify.PreOrderApi.FromBuyer.verify(request, pk)

        serializer = PreOrderSerializerUpdatePaymentShipping(pre_order, data=request.data, partial=True)
        if not serializer.is_valid():
            print (serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        pre_order = PreOrder.objects.get(id=pk)
        verify_message = Verify.PreOrderApi.FromBuyer.verify_delivery_info(pre_order)
        return Response(verify_message, status=status.HTTP_200_OK)

    # --------------------------------------------------------------------------------------------------------
    @action(detail=True, methods=['GET'], url_path=r'buyer_retrieve')
    @api_error_handler
    def buyer_retrieve_pre_order(self, request, pk=None):

        #OPERATION_CODE_NAME: AGILE
        # if request.user.id in settings.ADMIN_LIST:
        #     pre_order=PreOrder.objects.get(id=pk)
        #     serializer = PreOrderSerializer(pre_order)
        #     return Response(serializer.data, status=status.HTTP_200_OK)

        api_user, = getparams(request, (), with_user=True, seller=False)
        pre_order=Verify.get_pre_order(pk)
        Verify.user_match_pre_order(api_user, pre_order)

        # api_user, pre_order, order_product, campaign_product, qty = Verify.PreOrderApi.FromBuyer.verify(request, pk)
        serializer = PreOrderSerializer(pre_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_checkout')
    @api_error_handler
    def buyer_pre_order_checkout(self, request, pk=None):

        #OPERATION_CODE_NAME: AGILE
        # if request.user.id in settings.ADMIN_LIST:
        #     pre_order=PreOrder.objects.get(id=pk)
        #     api_order = PreOrderHelper.checkout(None, pre_order)
        #     return Response(api_order, status=status.HTTP_200_OK)

        api_user, = getparams(request, (), with_user=True, seller=False)
        pre_order=Verify.get_pre_order(pk)
        Verify.user_match_pre_order(api_user, pre_order)

        # api_user, pre_order, order_product, campaign_product, qty = Verify.PreOrderApi.FromBuyer.verify(request, pk)
        api_order = PreOrderHelper.checkout(api_user, pre_order)
        return Response(api_order, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_add')
    @api_error_handler
    def buyer_add_order_product(self, request, pk=None):

         #OPERATION_CODE_NAME: AGILE
        # if request.user.id in settings.ADMIN_LIST:
        #     campaign_product_id, qty = getparams(request, ('campaign_product_id', 'qty'),with_user=False)
        #     campaign_product = Campaign.objects.get(id=campaign_product_id)
        #     pre_order=PreOrder.objects.get(id=pk)
        #     api_order_product = PreOrderHelper.add_product(None, pre_order, campaign_product, qty)
        #     return Response(api_order_product, status=status.HTTP_200_OK)

        api_user, campaign_product_id, qty = getparams(request, ('campaign_product_id', 'qty'), with_user=True, seller=False)
        pre_order=Verify.get_pre_order(pk)
        Verify.user_match_pre_order(api_user, pre_order)
        campaign_product = Verify.get_campaign_product_from_pre_order(pre_order, campaign_product_id)

        # api_user, pre_order, order_product, campaign_product, qty = Verify.PreOrderApi.FromBuyer.verify(request, pk)
        api_order_product = PreOrderHelper.add_product(api_user, pre_order, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)


    @action(detail=True, methods=['POST'], url_path=r'buyer_bulk_add')
    @api_error_handler
    def buyer_buld_add_order_product(self, request, pk=None):
        error_message={}

         #OPERATION_CODE_NAME: AGILE
        # if request.user.id in settings.ADMIN_LIST:
        #     pre_order=PreOrder.objects.get(id=pk)
        #     for campaign_product_id,qty in request.data.items():
        #         try:
        #             campaign_product_id = int(campaign_product_id)
        #             campaign_product = pre_order.campaign.products.get(id=campaign_product_id)
        #             PreOrderHelper.add_product(None, pre_order, campaign_product, qty)
        #         except KeyError as e:
        #             print(e)
        #             error_message[campaign_product_id]=str(e)
        #         except ObjectDoesNotExist as e:
        #             print(e)
        #             error_message[campaign_product_id]=str(e)
        #         except PreOrderErrors.PreOrderException as e:
        #             print(e)
        #             error_message[campaign_product_id]=str(e)

        #         except ApiVerifyError as e:
        #             print(e)
        #             error_message[campaign_product_id]=str(e)
        #         except Exception as e:
        #             print(e)
        #             error_message[campaign_product_id]="server error"

        #     if error_message.em:
        #         return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

        #     return Response('success', status=status.HTTP_200_OK)

        
        api_user = Verify.get_customer_user(request)
        pre_order=PreOrder.objects.get(id=pk)
        Verify.user_match_pre_order(api_user, pre_order)

        for campaign_product_id,qty in request.data.items():
            try:
                campaign_product_id = int(campaign_product_id)
                campaign_product = pre_order.campaign.products.get(id=campaign_product_id)
                api_order_product = PreOrderHelper.add_product(api_user, pre_order, campaign_product, qty)
            except ApiVerifyError as e:
                print(e)
                error_message[campaign_product_id]=str(e)
            except Exception as e:
                print(e)
                error_message[campaign_product_id]="server error"


        if error_message:
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

        return Response('success', status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET'], url_path=r'buyer_update')
    @api_error_handler
    def buyer_update_order_product(self, request, pk=None):

        # OPERATION_CODE_NAME: AGILE
        # if request.user.id in settings.ADMIN_LIST:
        #     order_product_id, qty = getparams(request, ('order_product_id', 'qty'),with_user=False)
        #     order_product = OrderProduct.objects.get(id=order_product_id)
        #     pre_order=PreOrder.objects.get(id=pk)
        #     api_order_product = PreOrderHelper.update_product(
        #         None, pre_order, order_product, order_product.campaign_product, qty)
        #     return Response(api_order_product, status=status.HTTP_200_OK)
            
        api_user, order_product_id, qty = getparams(request, ('order_product_id', 'qty'), with_user=True, seller=False)
        pre_order=Verify.get_pre_order(pk)
        Verify.user_match_pre_order(api_user, pre_order)
        order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)
        api_order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, order_product.campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_delete')
    @api_error_handler
    def buyer_delete_order_product(self, request, pk=None):

        # OPERATION_CODE_NAME: AGILE
        # if request.user.id in settings.ADMIN_LIST:
        #     order_product_id, = getparams(request, ('order_product_id',),with_user=False)
        #     order_product = OrderProduct.objects.get(id=order_product_id)
        #     pre_order=PreOrder.objects.get(id=pk)
        #     PreOrderHelper.delete_product(
        #         None, pre_order, order_product, order_product.campaign_product)
        #     return Response({'message':"delete success"}, status=status.HTTP_200_OK)

        api_user, order_product_id = getparams(request, ('order_product_id',), with_user=True, seller=False)
        pre_order=Verify.get_pre_order(pk)
        Verify.user_match_pre_order(api_user, pre_order)
        order_product = Verify.get_order_product_from_pre_order(pre_order, order_product_id)
        PreOrderHelper.delete_product(
            api_user, pre_order, order_product, order_product.campaign_product)
        return Response({'message':"delete success"}, status=status.HTTP_200_OK)