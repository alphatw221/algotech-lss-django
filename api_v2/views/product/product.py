from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q

from rest_framework.parsers import MultiPartParser
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response


from api import models
from api import utils
from api.utils.error_handle.error_handler.api_error_handler import api_error_handler

from backend.pymongo.mongodb import db

import json

class ProductPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.product.product.Product.objects.all()
    serializer_class = models.product.product.ProductSerializer
    pagination_class = ProductPagination

    @action(detail=False, methods=['GET'], url_path=r'list', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_product(self, request):
        api_user, search_column, keyword, product_status, category = utils.common.common.getparams(request, ("search_column", "keyword", "product_status", "category"), with_user=True, seller=True)
        user_subscription = utils.common.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        kwargs = {}
        if (search_column in ["", None]) and (keyword not in [None, ""]):
            raise utils.common.verify.ApiVerifyError("search_column field can not be empty when keyword has value")
        if (search_column not in ['undefined', '']) and (keyword not in ['undefined', '', None]):
            kwargs = { search_column + '__icontains': keyword }
        if (category not in ['undefined', '', None]):
            kwargs['tag__contains'] = category
        
        kwargs['status'] = product_status

        queryset = user_subscription.products.all().order_by('id').filter(**kwargs)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'list/category', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_category(self, request):
        api_user, = utils.common.common.getparams(request, (), with_user=True, seller=True)
        user_subscription = utils.common.verify.Verify.get_user_subscription_from_api_user(api_user)

        categories_list = user_subscription.meta.get('categories', [])
        return Response(categories_list, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['POST'], url_path=r'create/category', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def create_category(self, request):
        api_user, category_name = utils.common.common.getparams(request, ("category_name", ), with_user=True, seller=True)
        user_subscription = utils.common.verify.Verify.get_user_subscription_from_api_user(api_user)

        categories_list = user_subscription.meta.get('categories', [])
        if category_name not in ['undefined', ''] and category_name not in categories_list:
            categories_list.append(category_name)
            user_subscription.meta['categories'] = categories_list
            user_subscription.save()

        return Response(categories_list, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['POST'], url_path=r'update/category', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_category(self, request):
        api_user, old_category, new_category = utils.common.common.getparams(request, ("old_category", "new_category"), with_user=True, seller=True)
        user_subscription = utils.common.verify.Verify.get_user_subscription_from_api_user(api_user)

        if old_category not in ['undefined', ''] and new_category not in ['undefined', '']:
            categories_list = user_subscription.meta.get('categories', [])
            categories_list = list(map(lambda x: x.replace(old_category, new_category), categories_list))            
            user_subscription.meta['categories'] = categories_list
            user_subscription.save()

        return Response(categories_list, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['DELETE'], url_path=r'delete/category', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def delete_category(self, request):
        api_user, category_name = utils.common.common.getparams(request, ("category_name", ), with_user=True, seller=True)
        user_subscription = utils.common.verify.Verify.get_user_subscription_from_api_user(api_user)

        categories_list = user_subscription.meta.get('categories', [])
        if category_name not in ['undefined', '']:
            categories_list.remove(category_name)
            user_subscription.meta['categories'] = categories_list
            user_subscription.save()

        return Response(categories_list, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['POST'], url_path=r'create_product', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @api_error_handler
    def create_product(self, request):
        api_user = utils.common.verify.Verify.get_seller_user(request)
        user_subscription = utils.common.verify.Verify.get_user_subscription_from_api_user(api_user)

        text = request.data['text']
        data = json.loads(text)
        data['user_subscription'] = user_subscription.id
        data['tag'] = data['categories']
        
        categories_list = user_subscription.meta.get('categories', [])
        for category in data['categories']:
            if category not in categories_list:
                categories_list.append(category)
                user_subscription.meta['categories'] = categories_list
                user_subscription.save()

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = serializer.save()

        image = request.data.get('image',None)
        if image:
            image_path = default_storage.save(
                f'{user_subscription.id}/product/{product.id}/{image.name}', ContentFile(image.read()))
            product.image = image_path

            product.save()

        return Response(models.product.product.ProductSerializer(product).data, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['PUT'], url_path=r'update_product', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_product(self, request, pk=None):

        api_user = utils.common.verify.Verify.get_seller_user(request)
        user_subscription = utils.common.verify.Verify.get_user_subscription_from_api_user(api_user)
        product = utils.common.verify.Verify.get_product_from_user_subscription(user_subscription, pk)

        text = request.data['text']
        data = json.loads(text)
        print (data)
        data['user_subscription'] = user_subscription.id
        data['tag'] = data['categories']
        
        categories_list = user_subscription.meta.get('categories', [])
        for category in data['categories']:
            if category not in categories_list:
                categories_list.append(category)
                user_subscription.meta['categories'] = categories_list
                user_subscription.save()

        image = request.data.get('image', None)

        if image:
            image_path = default_storage.save(
                f'{user_subscription.id}/product/{product.id}/{image.name}', ContentFile(image.read()))
            data['image'] = image_path
            
        serializer = models.product.product.ProductSerializer(
            product, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    