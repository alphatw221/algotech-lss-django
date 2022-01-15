import re
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from api.models.campaign.campaign import Campaign
from api.models.order.order_product import OrderProduct

from api.models.order.pre_order import PreOrder, PreOrderSerializer, PreOrderSerializerUpdatePaymentShipping
from api.utils.common.common import getparams
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError, platform_dict

from api.utils.common.order_helper import PreOrderHelper
from backend.pymongo.mongodb import db

from django.db.models import Q

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
        api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search = Verify.PreOrderApi.FromSeller.verify(request)
        serializer = PreOrderSerializer(pre_order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller_list')
    @api_error_handler
    def seller_list_pre_order(self, request):
        api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search = Verify.PreOrderApi.FromSeller.verify(request)
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

        api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search = Verify.PreOrderApi.FromSeller.verify(request,pk)
        api_order = PreOrderHelper.checkout(api_user, pre_order)
        return Response(api_order, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_add')
    @api_error_handler
    def seller_add_order_product(self, request, pk=None):
        api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search = Verify.PreOrderApi.FromSeller.verify(request, pk)
        api_order_product = PreOrderHelper.add_product(
            api_user, pre_order, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_update')
    @api_error_handler
    def seller_update_order_product(self, request, pk=None):
        api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search = Verify.PreOrderApi.FromSeller.verify(request, pk)
        api_order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'seller_delete')
    @api_error_handler
    def seller_delete_order_product(self, request, pk=None):
        api_user, platform, campaign, pre_order, order_product, campaign_product, qty, search = Verify.PreOrderApi.FromSeller.verify(request, pk)
        PreOrderHelper.delete_product(
            api_user, pre_order, order_product, campaign_product)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        pre_order = PreOrder.objects.get(id=pk)
        verify_message = Verify.PreOrderApi.FromBuyer.verify_delivery_info(pre_order)
        return Response(verify_message, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'buyer_retrieve')
    @api_error_handler
    def buyer_retrieve_pre_order(self, request, pk=None):

        #OPERATION_CODE_NAME: AGILE
        if request.user.id in settings.ADMIN_LIST:
            pre_order=PreOrder.objects.get(id=pk)
            serializer = PreOrderSerializer(pre_order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        api_user, pre_order, order_product, campaign_product, qty = Verify.PreOrderApi.FromBuyer.verify(request, pk)
        serializer = PreOrderSerializer(pre_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_checkout')
    @api_error_handler
    def buyer_pre_order_checkout(self, request, pk=None):

        #OPERATION_CODE_NAME: AGILE
        if request.user.id in settings.ADMIN_LIST:
            pre_order=PreOrder.objects.get(id=pk)
            api_order = PreOrderHelper.checkout(None, pre_order)
            return Response(api_order, status=status.HTTP_200_OK)

        api_user, pre_order, order_product, campaign_product, qty = Verify.PreOrderApi.FromBuyer.verify(request, pk)
        api_order = PreOrderHelper.checkout(api_user, pre_order)
        return Response(api_order, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_add')
    @api_error_handler
    def buyer_add_order_product(self, request, pk=None):

         #OPERATION_CODE_NAME: AGILE
        if request.user.id in settings.ADMIN_LIST:
            campaign_product_id, qty = getparams(request, ('campaign_product_id', 'qty'),with_user=False)
            campaign_product = Campaign.objects.get(id=campaign_product_id)
            pre_order=PreOrder.objects.get(id=pk)
            api_order_product = PreOrderHelper.add_product(None, pre_order, campaign_product, qty)
            return Response(api_order_product, status=status.HTTP_200_OK)

        api_user, pre_order, order_product, campaign_product, qty = Verify.PreOrderApi.FromBuyer.verify(request, pk)
        api_order_product = PreOrderHelper.add_product(api_user, pre_order, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)


    @action(detail=True, methods=['POST'], url_path=r'buyer_bulk_add')
    @api_error_handler
    def buyer_buld_add_order_product(self, request, pk=None):
        error_message={}

         #OPERATION_CODE_NAME: AGILE
        if request.user.id in settings.ADMIN_LIST:
            pre_order=PreOrder.objects.get(id=pk)
            for campaign_product_id,qty in request.data.items():
                try:
                    campaign_product_id = int(campaign_product_id)
                    campaign_product = pre_order.campaign.products.get(id=campaign_product_id)
                    PreOrderHelper.add_product(None, pre_order, campaign_product, qty)
                except KeyError as e:
                    print(e)
                    error_message[campaign_product_id]=str(e)
                except ObjectDoesNotExist as e:
                    print(e)
                    error_message[campaign_product_id]=str(e)
                except PreOrderErrors.PreOrderException as e:
                    print(e)
                    error_message[campaign_product_id]=str(e)

                except ApiVerifyError as e:
                    print(e)
                    error_message[campaign_product_id]=str(e)
                except Exception as e:
                    print(e)
                    error_message[campaign_product_id]="server error"

            if error_message.em:
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

            return Response('success', status=status.HTTP_200_OK)

        api_user = Verify.get_customer_user(request)
        pre_order=PreOrder.objects.get(id=pk)
        for campaign_product_id,qty in request.data.items():
            try:
                Verify.user_match_order(api_user, pre_order)
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
        if request.user.id in settings.ADMIN_LIST:
            order_product_id, qty = getparams(request, ('order_product_id', 'qty'),with_user=False)
            order_product = OrderProduct.objects.get(id=order_product_id)
            pre_order=PreOrder.objects.get(id=pk)
            api_order_product = PreOrderHelper.update_product(
                None, pre_order, order_product, order_product.campaign_product, qty)
            return Response(api_order_product, status=status.HTTP_200_OK)
            
        api_user, pre_order, order_product, campaign_product, qty = Verify.PreOrderApi.FromBuyer.verify(request, pk)
        api_order_product = PreOrderHelper.update_product(
            api_user, pre_order, order_product, campaign_product, qty)
        return Response(api_order_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'buyer_delete')
    @api_error_handler
    def buyer_delete_order_product(self, request, pk=None):

        # OPERATION_CODE_NAME: AGILE
        if request.user.id in settings.ADMIN_LIST:
            order_product_id, = getparams(request, ('order_product_id',),with_user=False)
            order_product = OrderProduct.objects.get(id=order_product_id)
            pre_order=PreOrder.objects.get(id=pk)
            PreOrderHelper.delete_product(
                None, pre_order, order_product, order_product.campaign_product)
            return Response({'message':"delete success"}, status=status.HTTP_200_OK)


        api_user, pre_order, order_product, campaign_product, qty = Verify.PreOrderApi.FromBuyer.verify(request, pk)
        PreOrderHelper.delete_product(
            api_user, pre_order, order_product, campaign_product)
        return Response({'message':"delete success"}, status=status.HTTP_200_OK)