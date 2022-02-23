from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from api.models.campaign.campaign_product import CampaignProduct, CampaignProductSerializer, CampaignProductSerializerUpdate
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from api.models.campaign.campaign_product import CampaignProductSerializer
from rest_framework.parsers import MultiPartParser

import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from api.models.product.product import Product

from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from api.utils.common.common import *

from datetime import datetime
from django.db.models import Q
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler

from api.utils.common.common import getdata, getparams

def verify_request(api_user, platform_name, platform_id, campaign_id, campaign_product_id=None, is_fast=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    campaign = Verify.get_campaign_from_platform(platform, campaign_id)
    user_subscription = Verify.get_user_subscription_from_platform(platform)

    if campaign_product_id:
        if not campaign.products.filter(id=campaign_product_id).exists():
            raise ApiVerifyError('no campaign product found')
        campaign_product = campaign.products.get(id=campaign_product_id)
        if is_fast == None:
            return platform, campaign, campaign_product
        else:
            return platform, campaign, campaign_product, user_subscription
    
    if is_fast:
        return platform, campaign, user_subscription

    return platform, campaign


class CampaignProductPagination(PageNumberPagination):

    page_size = 25
    page_query_param = 'page'
    page_size_query_param = 'page_size'

    # django_paginator_class - The Django Paginator class to use. Default is django.core.paginator.Paginator, which should be fine for most use cases.
    # page_size - A numeric value indicating the page size. If set, this overrides the PAGE_SIZE setting. Defaults to the same value as the PAGE_SIZE settings key.
    # page_query_param - A string value indicating the name of the query parameter to use for the pagination control.
    # page_size_query_param - If set, this is a string value indicating the name of a query parameter that allows the client to set the page size on a per-request basis. Defaults to None, indicating that the client may not control the requested page size.
    # max_page_size - If set, this is a numeric value indicating the maximum allowable requested page size. This attribute is only valid if page_size_query_param is also set.
    # last_page_strings - A list or tuple of string values indicating values that may be used with the page_query_param to request the final page in the set. Defaults to ('last',)
    # template - The name of a template to use when rendering pagination controls in the browsable API. May be overridden to modify the rendering style, or set to None to disable HTML pagination controls completely. Defaults to "rest_framework/pagination/numbers.html".


class CampaignProductViewSet(viewsets.ModelViewSet):
    queryset = CampaignProduct.objects.all().order_by('id')
    serializer_class = CampaignProductSerializer
    filterset_fields = []
    pagination_class = CampaignProductPagination

    @action(detail=True, methods=['GET'], url_path=r'retrieve_campaign_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def retrieve_campaign_product(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        campaign_id = request.query_params.get('campaign_id')
        api_user = request.user.api_users.get(type='user')

        _, _, campaign_product = verify_request(
            api_user, platform_name, platform_id, campaign_id, campaign_product_id=pk)

        serializer = self.get_serializer(campaign_product)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_campaign_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_campaign_product(self, request):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        campaign_id = request.query_params.get('campaign_id')
        order_by = request.query_params.get('order_by')
        product_status = request.query_params.get('status')
        type = request.query_params.get('type')
        # exclude = request.query_params.get('exclude')
        key_word = request.query_params.get('key_word')
        api_user = request.user.api_users.get(type='user')
        _, campaign = verify_request(
            api_user, platform_name, platform_id, campaign_id)
        # print(campaign)
        campaign_products = campaign.products.all()

        if product_status:
            campaign_products = campaign_products.filter(
                status=product_status)
        if type:
            campaign_products = campaign_products.filter(
                type__icontains=type)
        if key_word:
            campaign_products = campaign_products.filter(
                name__icontains=key_word)
        if order_by:
            campaign_products = campaign_products.order_by(order_by)

        if request.query_params.get('page'):
            page = self.paginate_queryset(campaign_products)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data
            else:
                serializer = self.get_serializer(
                    campaign_products, many=True)
                data = serializer.data
        else:
            serializer = self.get_serializer(campaign_products, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_campaign_lucky_draw_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_campaign_lucky_draw_product(self, request):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        campaign_id = request.query_params.get('campaign_id')
        api_user = request.user.api_users.get(type='user')
        _, campaign = verify_request(
            api_user, platform_name, platform_id, campaign_id)

        campaign_products = campaign.products.filter(Q(type='lucky_draw') | Q(type="lucky_draw-fast"))


        serializer = self.get_serializer(campaign_products, many=True)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_campaign_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def create_campaign_product(self, request):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        campaign_id = request.query_params.get('campaign_id')
        api_user = request.user.api_users.get(type='user')

        _, campaign = verify_request(
            api_user, platform_name, platform_id, campaign_id)

        data = request.data
        data['campaign'] = campaign.id
        data['created_by'] = api_user.id
        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update_campaign_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_campaign_product(self, request, pk=None):


        api_user, platform_id, platform_name, campaign_id = getparams(request, ("platform_id","platform_name","campaign_id"), with_user=True, seller=True)
        
        platform = Verify.get_platform(api_user, platform_name, platform_id)
        campaign = Verify.get_campaign_from_platform(platform, campaign_id)
        campaign_product = Verify.get_campaign_product_from_campaign(campaign, pk)

       
        if "price" in request.data and campaign.start_at and datetime.timestamp(datetime.now())>datetime.timestamp(campaign.start_at):
            raise ApiVerifyError('price not editable after starting campaign')

        serializer = CampaignProductSerializerUpdate(
            campaign_product, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        # serializer = CampaignProductSerializer(campai)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete_campaign_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def delete_campaign_product(self, request, pk=None):

        api_user, platform_id, platform_name, campaign_id = getparams(request,("platform_id", "platform_name", "campaign_id"), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        campaign = Verify.get_campaign_from_platform(platform, campaign_id)
        campaign_product = Verify.get_campaign_product_from_campaign(campaign, pk)

        if campaign.start_at and datetime.timestamp(datetime.now())>datetime.timestamp(campaign.start_at):
            raise ApiVerifyError('campaign product not deletable after starting campaign')
        
        #soft delete:
        campaign_product.campaign = None
        campaign_product.save()

        #hard delete:
        # campaign_product.delete()

        # Verify.get_campaign_product_from_campaign(campaign, pk)
        # platform_id = request.query_params.get('platform_id')
        # platform_name = request.query_params.get('platform_name')
        # campaign_id = request.query_params.get('campaign_id')
        # api_user = request.user.api_users.get(type='user')

        # _, _, campaign_product = verify_request(
        #     api_user, platform_name, platform_id, campaign_id, campaign_product_id=pk)

        # campaign_product.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['POST'], url_path=r'fast_add_product', permission_classes=(IsAuthenticated,) )
    @api_error_handler
    def fast_add_product(self, request):

        api_user, platform_id, platform_name, campaign_id, code, price, qty = getparams(request, ("platform_id", "platform_name", "campaign_id", "code", "price", "qty"), with_user=True, seller=True)

        platform = Verify.get_platform(api_user, platform_name, platform_id)
        campaign = Verify.get_campaign_from_platform(platform, campaign_id)
        user_subscription = Verify.get_user_subscription_from_platform(platform)

        product = Product.objects.create(user_subscription=user_subscription, created_by=api_user, name=code, order_code=code, price=float(price), qty=0)
        campaign_product = CampaignProduct.objects.create(campaign=campaign, created_by=api_user,product=product,  status=1, type='product-fast', name=code, order_code=code, price=float(price), qty_for_sale=int(qty))

        return Response(CampaignProductSerializer(campaign_product).data, status=status.HTTP_200_OK)


        # _, campaign, user_subscription = verify_request(
        #     api_user, platform_name, platform_id, campaign_id, is_fast=True)

        # text = request.data['text']
        # data = json.loads(text)
        # data['campaign'] = campaign.id
        # data['created_by'] = api_user.id
        # data['user_subscription'] = user_subscription.id
        # serializer = self.get_serializer(data=data)

        # if not serializer.is_valid():
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # fast_campaign = serializer.save()

        # if 'image' in request.data:
        #     image = request.data['image']
        #     image_path = default_storage.save(
        #         f'{user_subscription.id}/fast_campaign/{fast_campaign.id}/{image.name}', ContentFile(image.read()))
        #     fast_campaign.image = image_path

        #     fast_campaign.save()    

        # return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'fast_update', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @api_error_handler
    def fast_update_campaign_product(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        campaign_id = request.query_params.get('campaign_id')
        api_user = request.user.api_users.get(type='user')

        _, campaign, campaign_product, user_subscription = verify_request(
            api_user, platform_name, platform_id, campaign_id, campaign_product_id=pk, is_fast=True)

        if 'image' in request.data:
            image = request.data['image']
            image_path = default_storage.save(
                f'{user_subscription.id}/fast_campaign/{campaign_product.id}/{image.name}', ContentFile(image.read()))

        text = request.data['text']
        data = json.loads(text)
        data['image'] = image_path

        serializer = CampaignProductSerializerUpdate(
            campaign_product, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


    #----------------------------------------------buyer--------------------------------------------------


    @action(detail=False, methods=['GET'], url_path=r'buyer_list_campaign_product')
    @api_error_handler
    def buyer_list_campaign_product(self, request):
        # api_user, pre_order_id = getparams(request,('pre_order_id',), seller=False)
        pre_order_id = request.query_params.get('pre_order_id')
        pre_order=Verify.get_pre_order(pre_order_id)
        # Verify.user_match_pre_order(api_user, pre_order)

        campaign_products = pre_order.campaign.products.filter(Q(type='product') | Q(type="product-fast"))
        serializer = self.get_serializer(campaign_products, many=True)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path=r'campaign_prodcut_list')
    @api_error_handler
    def buyer_campaign_prodcut_list(self, request, pk=None):
        pre_order = Verify.get_pre_order(pk)
        campaign_products = pre_order.campaign.products.values()
        return Response(campaign_products, status=status.HTTP_200_OK)