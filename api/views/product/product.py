import imp
from logging import exception
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from api.models.product.product import Product, ProductSerializer, ProductSerializerDropdown
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from backend.pymongo.mongodb import db
from backend.pymongo.mongodb import get_incremented_filed

import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from api.utils.common.common import *

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler

def verify_request(api_user, platform_name, platform_id, product_id=None):
    Verify.verify_user(api_user)
    platform = Verify.get_platform(api_user, platform_name, platform_id)
    user_subscription = Verify.get_user_subscription(platform)
    if product_id:
        if not user_subscription.products.filter(id=product_id).exists():
            raise ApiVerifyError('no product found')
        product = user_subscription.products.get(id=product_id)
        return platform, user_subscription, product

    return platform, user_subscription


class ProductPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'

    # django_paginator_class - The Django Paginator class to use. Default is django.core.paginator.Paginator, which should be fine for most use cases.
    # page_size - A numeric value indicating the page size. If set, this overrides the PAGE_SIZE setting. Defaults to the same value as the PAGE_SIZE settings key.
    # page_query_param - A string value indicating the name of the query parameter to use for the pagination control.
    # page_size_query_param - If set, this is a string value indicating the name of a query parameter that allows the client to set the page size on a per-request basis. Defaults to None, indicating that the client may not control the requested page size.
    # max_page_size - If set, this is a numeric value indicating the maximum allowable requested page size. This attribute is only valid if page_size_query_param is also set.
    # last_page_strings - A list or tuple of string values indicating values that may be used with the page_query_param to request the final page in the set. Defaults to ('last',)
    # template - The name of a template to use when rendering pagination controls in the browsable API. May be overridden to modify the rendering style, or set to None to disable HTML pagination controls completely. Defaults to "rest_framework/pagination/numbers.html".


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = []
    pagination_class = ProductPagination

    @action(detail=True, methods=['GET'], url_path=r'retrieve_product')
    @api_error_handler
    def retrieve_product(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        _, _, product = verify_request(
            api_user, platform_name, platform_id, product_id=pk)

        serializer = self.get_serializer(product)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_product')
    @api_error_handler
    def list_product(self, request):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        order_by = request.query_params.get('order_by')
        product_status = request.query_params.get('status')
        key_word = request.query_params.get('key_word')
        api_user = request.user.api_users.get(type='user')

        _, user_subscription = verify_request(
            api_user, platform_name, platform_id)

        queryset = user_subscription.products.all()
        if product_status:
            queryset = queryset.filter(status=product_status)
        if key_word:
            queryset = queryset.filter(name__icontains=key_word)
        if order_by:
            queryset = queryset.order_by(order_by)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_product', parser_classes=(MultiPartParser,))
    @api_error_handler
    def create_product(self, request):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        _, user_subscription = verify_request(
            api_user, platform_name, platform_id)

        text = request.data['text']
        data = json.loads(text)
        data['user_subscription'] = user_subscription.id
        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = serializer.save()

        if 'image' in request.data:
            image = request.data['image']
            image_path = default_storage.save(
                f'{user_subscription.id}/product/{product.id}/{image.name}', ContentFile(image.read()))
            product.image = image_path

            product.save()

        return Response(self.get_serializer(product).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update_product', parser_classes=(MultiPartParser,))
    @api_error_handler
    def update_product(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        _, user_subscription, product = verify_request(
            api_user, platform_name, platform_id, product_id=pk)

        text = request.data['text']
        data = json.loads(text)

        if 'image' in request.data:
            image = request.data['image']
            image_path = default_storage.save(
                f'{user_subscription.id}/product/{product.id}/{image.name}', ContentFile(image.read()))
            data['image'] = image_path

        serializer = ProductSerializer(
            product, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete_product')
    @api_error_handler
    def delete_product(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        _, _, product = verify_request(
            api_user, platform_name, platform_id, product_id=pk)

        # TODO put it into private bucket
        # if product.image:
        #     default_storage.delete(product.image)
        product.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['DELETE'], url_path=r'delete_multiple_product')
    @api_error_handler
    def delete_product(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        _, _ = verify_request(
            api_user, platform_name, platform_id)
        
        product_list = request.data['product_list']
        db.api_product.update_many({'id': {'$in': product_list}}, {'$set': {'status': 'archived'}})

        return Response({"message": "delete multiple products success"}, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['GET'], url_path=r'update_product_to_campaign')
    @api_error_handler
    def update_product_to_campaign(self, request, pk=None):
        campaign_id = request.query_params.get('campaign_id')
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')
        order_code = request.query_params.get('order_code')
        max_order_amount = request.query_params.get('max_order_amount')
        qty_for_sale = request.query_params.get('qty_for_sale')
        customer_removable = 1 if request.query_params.get('customer_removable') == "1" else 0
        customer_editable = 1 if request.query_params.get('customer_editable') == "1" else 0

        _, _, product = verify_request(
            api_user, platform_name, platform_id, product_id=pk)
        
        p_datas, _id = db.api_campaign_product.find({'campaign_id': int(campaign_id)}).sort([('id', -1)]).limit(1), 0
        for p in p_datas:
            _id = int(p['id']) + 1

        product_dict = product.__dict__
        product_dict['product_id'] = int(product_dict['id'])
        product_dict['order_code'] = order_code
        product_dict['max_order_amount'] = int(max_order_amount)
        product_dict['qty_for_sale'] = int(qty_for_sale)
        product_dict['qty_sold'] = 0
        product_dict['customer_removable'] = bool(customer_removable)
        product_dict['customer_editable'] = bool(customer_editable)
        product_dict['campaign_id'] = int(campaign_id)
        product_dict['status'] = 0
        product_dict.pop('_state', None)
        product_dict.pop('id', None)

        db.api_campaign_product.update({'id': _id}, {'$set': product_dict}, upsert=True)
        campaign_product = db.api_campaign_product.find_one({'id': _id})
        campaign_product.pop('_id', None)

        return Response(campaign_product, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'archive_product')
    @api_error_handler
    def archive_product(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')
        data = request.data

        _, _, product = verify_request(
            api_user, platform_name, platform_id, product_id=pk)

        serializer = ProductSerializer(
            product, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response({"message": "product archive success"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'update_image',  parser_classes=(MultiPartParser,))
    @api_error_handler
    def update_image(self, request, pk=None):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        _, user_subscription, product = verify_request(
            api_user, platform_name, platform_id, product_id=pk)

        if 'image' in request.data:
            image = request.data['image']
            image_path = default_storage.save(
                f'{user_subscription.id}/product/{product.id}/{image.name}', ContentFile(image.read()))
            product.image = image_path
            product.save()

        return Response(product.image, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'product_dropdown')
    @api_error_handler
    def product_dropdown(self, request):
        platform_id = request.query_params.get('platform_id')
        platform_name = request.query_params.get('platform_name')
        api_user = request.user.api_users.get(type='user')

        _, user_subscription = verify_request(
            api_user, platform_name, platform_id)

        products = user_subscription.products.filter(
            status='enabled').all()
        serializer = ProductSerializerDropdown(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
