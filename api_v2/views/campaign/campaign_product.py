from configparser import MAX_INTERPOLATION_DEPTH
import traceback
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from django.db.models import Q

from api import models
from api import utils

import lib
from datetime import datetime
import database

class CampaignProductPagination(PageNumberPagination):

    page_size = 25
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class CampaignProductViewSet(viewsets.ModelViewSet):
    queryset = models.campaign.campaign_product.CampaignProduct.objects.all().order_by('id')
    serializer_class = models.campaign.campaign_product.CampaignProductSerializer
    filterset_fields = []
    pagination_class = CampaignProductPagination

#----------------------------------------------guest--------------------------------------------------

    @action(detail=False, methods=['GET'], url_path=r'guest/list', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_list(self, request):
        pre_order_oid = request.query_params.get('pre_order_oid')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        campaign_products = pre_order.campaign.products.filter(Q(type='product') | Q(type="product-fast"))
        
        return Response(models.campaign.campaign_product.CampaignProductSerializer(campaign_products, many=True).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'guest/cart/list', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def guest_prodcut_list(self, request):
        pre_order_oid = request.query_params.get('pre_order_oid')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        
        return Response(models.campaign.campaign_product.CampaignProductSerializer(pre_order.campaign.products, many=True).data, status=status.HTTP_200_OK)

#----------------------------------------------buyer--------------------------------------------------


    @action(detail=False, methods=['GET'], url_path=r'buyer/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_list(self, request):
        pre_order_oid = request.query_params.get('pre_order_oid')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        campaign_products = pre_order.campaign.products.filter(Q(type='product') | Q(type="product-fast"))
        
        return Response(models.campaign.campaign_product.CampaignProductSerializer(campaign_products, many=True).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path=r'buyer/cart/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_prodcut_list(self, request):
        pre_order_oid = request.query_params.get('pre_order_oid')
        pre_order = lib.util.verify.Verify.get_pre_order_with_oid(pre_order_oid)
        
        return Response(models.campaign.campaign_product.CampaignProductSerializer(pre_order.campaign.products, many=True).data, status=status.HTTP_200_OK)


#----------------------------------------------seller--------------------------------------------------

    @action(detail=False, methods=['POST'], url_path=r'seller/create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_create_campaign_product(self, request):
        api_user, campaign_id = lib.util.getter.getparams(request, ("campaign_id", ), with_user=True, seller=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        campaign_products_data = request.data
        errors = []

        new_products = []
        for campaign_product_data in campaign_products_data:
            try:
                product = lib.util.verify.Verify.get_product_from_user_subscription(user_subscription, campaign_product_data.get('product_id'))
                print(product)
                serializer = models.campaign.campaign_product.CampaignProductSerializerAssign(data=campaign_product_data)
                if not serializer.is_valid():
                    errors.append({"product_id": campaign_product_data.get('product_id')})
                    continue
                campaign_product = serializer.save()

                campaign_product.campaign = campaign
                campaign_product.product = product
                campaign_product.created_by = api_user
                campaign_product.save()
                new_products.append(campaign_product)
            except lib.error_handle.error.api_error.ApiVerifyError as e:
                errors.append({"product_id": campaign_product_data.get('product_id')})
                continue
        serializer = self.get_serializer(new_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path=r'seller/create/bulk', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_bulk_create_campaign_product(self, request):
        api_user, campaign_id = lib.util.getter.getparams(request, ("campaign_id", ), with_user=True, seller=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        try:
            with database.lss.util.start_session() as session:
                with session.start_transaction():
                    data = {'message':'Invalid','errors':[]}
                    got_error=False
                    order_code_set = set()
                    api_campaign_products = database.lss.campaign_product.CampaignProduct.filter(campaign_id=campaign.id, session=session)
                    for api_campaign_product in api_campaign_products:
                        order_code_set.add(api_campaign_product.get('order_code'))

                    if not request.data:
                        got_error = True
                        data['message']='Invalid'
                    for request_data in request.data :
                        e = {}

                        api_product = database.lss.product.Product.get_object(id=request_data.get('id'), user_subscription_id=user_subscription.id, session=session)
                        if not api_product:
                            e['name']='no product found'
                            data.get('errors').append(e)
                            got_error = True
                            continue
                        if request_data.get('type') not in [models.campaign.campaign_product.TYPE_PRODUCT,models.campaign.campaign_product.TYPE_LUCKY_DRAW]:
                            e['type'] = 'type_invalid'
                            data.get('errors').append(e)
                            got_error = True
                            continue

                        if request_data.get('type')==models.campaign.campaign_product.TYPE_PRODUCT and request_data.get('order_code') in order_code_set:
                            e['order_code']='order_code_duplicate'
                            got_error = True
                        else:
                            order_code_set.add(request_data.get('order_code'))

                        if not request_data.get('assign_qty'):
                            e['assign_qty']='invalid_qty'
                            got_error = True

                        # elif api_product.data.get('qty') < request_data.get('qty'):
                        #     e['qty']=f"only {api_product.data.get('qty')} left"
                        #     got_error = True
                        max_order_amount = request_data.get('max_order_amount') if request_data.get('max_order_amount') else 0
                        max_order_amount = int(max_order_amount)
                        if request_data.get('type')==models.campaign.campaign_product.TYPE_PRODUCT and max_order_amount > request_data.get('assign_qty'):
                            e['max_order_amount']='max_order_amount_grater_than_qty'
                            got_error = True
                        
                        data.get('errors').append(e)

                        if not e:
                            data.get('errors').append(None)
                            qty_for_sale = int(request_data.get('assign_qty', 0)) if request_data.get('assign_qty') else 0
                            api_product.distribute(qty_for_sale, sync=False, session=session)
                            database.lss.campaign_product.CampaignProduct.create(
                                image = str(request_data.get('image')),
                                name=str(request_data.get('name', '')), 
                                order_code=str(request_data.get('order_code', '')), 
                                qty_for_sale=qty_for_sale, 
                                max_order_amount=int(request_data.get('max_order_amount')) if request_data.get('max_order_amount') else 0, 
                                price=float(request_data.get('price', 0)) if request_data.get('price') else 0, 
                                customer_editable=bool(request_data.get('customer_editable', True)), 
                                customer_removable=bool(request_data.get('customer_removable', True)),
                                tag=list(request_data.get('tag',[])),
                                type=str(request_data.get('type',models.product.product.TYPE_PRODUCT)),
                                product_id = int(request_data.get('id')) if request_data.get('id') else None,
                                campaign_id=campaign.id,
                                session=session)

                    if got_error:
                        print(data)
                        raise Exception()

            

        except Exception :
            print(traceback.format_exc())
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(models.campaign.campaign_product.CampaignProductSerializer(campaign.products, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'seller/list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_retrieve_campaign_products(self, request):
        api_user, campaign_id, category = lib.util.getter.getparams(request, ("campaign_id", "category"), with_user=True, seller=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign = lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)

        kwargs = {'tag__icontains':category} if category not in ['undefined', '', None, 'null'] else {}
        queryset = campaign.products.filter(**kwargs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = models.campaign.campaign_product.CampaignProductSerializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = models.campaign.campaign_product.CampaignProductSerializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['DELETE'], url_path=r'seller/delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_campaign_product(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign_product = lib.util.verify.Verify.get_campaign_product(pk)
        campaign = campaign_product.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        if campaign.start_at and datetime.timestamp(datetime.now()) > datetime.timestamp(campaign.start_at):
            raise lib.error_handle.error.api_error.ApiVerifyError("This campaign product can't be deleted because the campaign has already started.")
        
        ## soft delete:
        campaign_product.campaign = None
        campaign_product.save()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['PUT'], url_path=r'seller/update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_campaign_product(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign_product = lib.util.verify.Verify.get_campaign_product(pk)
        campaign = campaign_product.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        if campaign.start_at and datetime.timestamp(datetime.now()) > datetime.timestamp(campaign.start_at):
            raise lib.error_handle.error.api_error.ApiVerifyError("This campaign product can't be edited because the campaign has already started.")

        serializer = models.campaign.campaign_product.CampaignProductSerializerUpdate(
            campaign_product, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        serializer = models.campaign.campaign_product.CampaignProductSerializer(campaign_product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PUT'], url_path=r'seller/toggle/status', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def toggle_campaign_product_status(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        campaign_product = lib.util.verify.Verify.get_campaign_product(pk)
        campaign = campaign_product.campaign
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription, campaign.id)

        campaign_product.status = not campaign_product.status
        campaign_product.save()

        serializer = models.campaign.campaign_product.CampaignProductSerializer(campaign_product)
        return Response(serializer.data, status=status.HTTP_200_OK)