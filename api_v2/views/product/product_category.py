
from platform import platform
from django.core.files.base import ContentFile
from django.conf import settings

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from api.models.product import product_category

from automation import jobs

from api import models
from api_v2 import rule
import database

import lib, json


class ProductCatoegoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = models.product.product_category.ProductCategory.objects.all()
    serializer_class = models.product.product_category.ProductCategorySerializer

    @action(detail=False, methods=['GET'], url_path=r'list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_product_category(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product_categories = user_subscription.product_categories.all()
        data = models.product.product_category.ProductCategorySerializer(product_categories, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_product_cateogry(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product_category = lib.util.verify.Verify.get_product_category_from_user_subscription(user_subscription, pk)
        data = models.product.product_category.ProductCategorySerializer(product_category).data
        return Response(data, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['POST'], url_path=r'create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_product_category(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        request.data['user_subscription'] = user_subscription.id
        serializer = models.product.product_category.ProductCategorySerializer(data = request.data)
        if not serializer.is_valid():
            raise lib.error_handle.error.api_error.ApiVerifyError('duplicate_product_category_name')

        product_category = serializer.save()
        data = models.product.product_category.ProductCategorySerializer(product_category).data
        return Response(data, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['PUT'], url_path=r'update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_product_category(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product_category = lib.util.verify.Verify.get_product_category_from_user_subscription(user_subscription, pk)

        serializer = models.product.product_category.ProductCategorySerializerUpdate(product_category, data=request.data, partial=True)
        if not serializer.is_valid():
            raise lib.error_handle.error.api_error.ApiVerifyError('duplicate_product_category_name')

        product_category = serializer.save()
        data = models.product.product_category.ProductCategorySerializer(product_category).data
        
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['DELETE'], url_path=r'delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_product_category(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product_category = lib.util.verify.Verify.get_product_category_from_user_subscription(user_subscription, pk)
        

        #unset all product and campaign product categories key
        database.lss.product.remove_categories(product_category.id)
        database.lss.campaign_product.remove_categories(product_category.id)
        product_category.delete()
        return Response({"message": "delete success"}, status=status.HTTP_200_OK)

    
    
    

    
    
    
    