from unicodedata import category
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from api import utils

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from api import models
import lib, json
from api import rule

class ProductPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.product.product.Product.objects.all()
    serializer_class = models.product.product.ProductSerializer
    pagination_class = ProductPagination

    @action(detail=False, methods=['GET'], url_path=r'search', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_product(self, request):
        api_user, search_column, keyword, product_status, category = \
            lib.util.getter.getparams(request, ("search_column", "keyword", "product_status", "category"), with_user=True, seller=True)

        user_subscription = \
            lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        kwargs = {'status': product_status if product_status else 'enabled'}
        if (search_column in ["", None]) and (keyword not in [None, ""]):
            raise lib.error_handle.error.api_error.ApiVerifyError("search_column field can not be empty when keyword has value")
        if (search_column not in ['undefined', '']) and (keyword not in ['undefined', '', None]):
            kwargs = { search_column + '__icontains': keyword }
        if category not in ['undefined', '', None]:
            kwargs = { 'tag__icontains': category }

        queryset = user_subscription.products.filter(**kwargs).order_by("-created_at")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_product(self, request, pk):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product = lib.util.verify.Verify.get_product_from_user_subscription(user_subscription, pk)

        return Response(models.product.product.ProductSerializer(product).data, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['POST'], url_path=r'create', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_product(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        image, category = lib.util.getter.getdata(request,('image', 'category'), required=False)
        data, = lib.util.getter.getdata(request,('data',),required=True)
        data = json.loads(data)

        rule.rule_checker.product_rule_checker.ProductCreateRuleChecker.check(product_data=data)

        serializer=models.product.product.ProductSerializerCreate(data = data) 
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = serializer.save()
        
        if image:
            image_path = default_storage.save(
                f'{user_subscription.id}/product/{product.id}/{image.name}', ContentFile(image.read()))
            product.image = image_path
        
        product.user_subscription = user_subscription
        product.category = category if category else None
        product.save()

        product_categories = user_subscription.meta.get('product_categories', [])
        if category and category not in product_categories:
            product_categories.append(category)
            user_subscription.meta['product_categories'] = product_categories
            user_subscription.save()

        return Response(models.product.product.ProductSerializer(product).data, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['PUT'], url_path=r'update', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_product(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product = lib.util.verify.Verify.get_product_from_user_subscription(user_subscription, pk)

        image, category = lib.util.getter.getdata(request,('image', 'category'), required=False)
        data, = lib.util.getter.getdata(request,('data',),required=True)
        data = json.loads(data)
        
        rule.rule_checker.product_rule_checker.ProductCreateRuleChecker.check(product_data=data)

        serializer=models.product.product.ProductSerializerUpdate(product, data=data, partial=True) 
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = serializer.save()

        if image:
            image_path = default_storage.save(
                f'{user_subscription.id}/product/{product.id}/{image.name}', ContentFile(image.read()))
            product.image = image_path

        product.category = category if category else None
        product.save()

        product_categories = user_subscription.meta.get('product_categories', [])
        if category and category not in product_categories:
            product_categories.append(category)
            user_subscription.meta['product_categories'] = product_categories
            user_subscription.save()

        return Response(models.product.product.ProductSerializer(product).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_product(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product = lib.util.verify.Verify.get_product_from_user_subscription(user_subscription, pk)

        product.delete()
        return Response({"message": "delete success"}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'], url_path=r'categories', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_category(self, request):
        api_user, = lib.util.getter.getparams(request, (), with_user=True, seller=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        product_categories = user_subscription.meta.get('product_categories', [])
        return Response(product_categories, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['POST'], url_path=r'category/create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_category(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        category_name, = lib.util.getter.getdata(request, ('category_name',), required=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product_categories = user_subscription.meta.get('product_categories',[])
        
        if category_name in product_categories:
            raise lib.error_handle.error.api_error.ApiVerifyError("category already exists")
        product_categories.append(category_name)
        user_subscription.meta['product_categories'] = product_categories
        user_subscription.save()

        return Response(product_categories, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['PUT'], url_path=r'category/update/(?P<category_name>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_category(self, request, category_name):
        
        api_user = lib.util.verify.Verify.get_seller_user(request)
        update_name, = lib.util.getter.getdata(request, ('category_name',), required=True)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        if category_name in ['undefined', '', None] or update_name in ['undefined', '', None]:
            raise lib.error_handle.error.api_error.ApiVerifyError("invalid category name")
        
        categories_list = user_subscription.meta.get('product_categories', [])

        if category_name not in categories_list:
            raise lib.error_handle.error.api_error.ApiVerifyError("category doesn't exists ")

        categories_list = list(map(lambda x: x.replace(category_name, update_name), categories_list))            
        user_subscription.meta['product_categories'] = categories_list
        user_subscription.save()

        models.product.product.Product.objects.filter(user_subscription=user_subscription, category=category_name ).update(category=update_name)

        return Response(categories_list, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['DELETE'], url_path=r'category/delete/(?P<category_name>[^/.]+)', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_category(self, request, category_name):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        if category_name in ['undefined', '', None] :
            raise lib.error_handle.error.api_error.ApiVerifyError("invalid category name")

        categories_list = user_subscription.meta.get('product_categories', [])

        if category_name not in categories_list:
            raise lib.error_handle.error.api_error.ApiVerifyError("category doesn't exists ")
            
        categories_list.remove(category_name)
        user_subscription.meta['product_categories'] = categories_list
        user_subscription.save()

        models.product.product.Product.objects.filter(user_subscription=user_subscription, category=category_name ).delete()

        return Response(categories_list, status=status.HTTP_200_OK)