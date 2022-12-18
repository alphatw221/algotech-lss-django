from django.core.files.base import ContentFile
from django.conf import settings

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import action
from rest_framework.response import Response


from automation import jobs

from api import models
from api_v2 import rule

import factory
import lib, json
class ProductPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    sort_query_param = 'sort_by'


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = models.product.product.Product.objects.all()
    serializer_class = models.product.product.ProductSerializer
    pagination_class = ProductPagination

    @action(detail=False, methods=['GET'], url_path=r'search', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def search_product(self, request):
        api_user, support_stock_user_subscription_id, search_column, keyword, product_status, product_type, category_id, exclude_products, sort_by = \
            lib.util.getter.getparams(request, ("support_stock_user_subscription_id", "search_column", "keyword", "product_status", "product_type", "category_id", "exclude", "sort_by"), with_user=True, seller=True)
        user_subscription = \
            lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        if support_stock_user_subscription_id not in ["", None, "null", "undefined"]:
            user_subscription = lib.util.verify.Verify.get_support_stock_user_subscriptions_from_user_subscription(support_stock_user_subscription_id,user_subscription)
        
        
        kwargs = {'status': product_status if product_status else 'enabled'}
        if (search_column in ["", None]) and (keyword not in [None, ""]):
            raise lib.error_handle.error.api_error.ApiVerifyError("search_can_not_empty")
        if (search_column not in ['undefined', '']) and (keyword not in ['undefined', '', None]):
            kwargs[search_column + '__icontains'] = keyword
        if ( product_type in [models.product.product.TYPE_PRODUCT, models.product.product.TYPE_LUCY_DRAW]):
            kwargs['type'] = product_type
        if category_id not in ['undefined', '', None]:
            kwargs['categories__icontains'] = category_id 
        
        if(sort_by in ['undefined', '', None]):
            queryset = user_subscription.products.filter(**kwargs).order_by("-updated_at")
        else: 
            queryset = user_subscription.products.filter(**kwargs).order_by(sort_by)
        
        if exclude_products:
            exclude_products = exclude_products.split(",")
            queryset = queryset.exclude(id__in=exclude_products)
            
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

        image, = lib.util.getter.getdata(request,('image', ), required=False)
        data, = lib.util.getter.getdata(request,('data',),required=True)
        data = json.loads(data)

        data['user_subscription'] = user_subscription.id
        rule.rule_checker.product_rule_checker.RuleChecker.check(check_list=[
            rule.check_rule.product_check_rule.ProductCheckRule.is_max_order_amount_less_than_qty,
            rule.check_rule.product_check_rule.ProductCheckRule.is_images_type_supported,
            rule.check_rule.product_check_rule.ProductCheckRule.is_images_exceed_max_size
        ],product_data=data, image=image)

        serializer=models.product.product.ProductSerializer(data = data) 
        if not serializer.is_valid():
            print(data)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = serializer.save()

        if image in ['null', None, '', 'undefined']:
            pass
        elif image =='._no_image':
            product.image = settings.GOOGLE_STORAGE_STATIC_DIR+models.product.product.IMAGE_NULL
            product.save()
        else:
            image_name = image.name.replace(" ","")
            image_dir = f'user_subscription/{user_subscription.id}/product/{product.id}'
            image_url = lib.util.storage.upload_image(image_dir, image_name, image)
            product.image = image_url
            product.save()

 

        return Response(models.product.product.ProductSerializer(product).data, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['PUT'], url_path=r'update', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_product(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product = lib.util.verify.Verify.get_product_from_user_subscription(user_subscription, pk)

        image, = lib.util.getter.getdata(request,('image', ), required=False)
        data, = lib.util.getter.getdata(request,('data',),required=True)
        data = json.loads(data)

        rule.rule_checker.product_rule_checker.RuleChecker.check(check_list=[
            rule.check_rule.product_check_rule.ProductCheckRule.is_max_order_amount_less_than_qty,
            rule.check_rule.product_check_rule.ProductCheckRule.is_images_type_supported,
            rule.check_rule.product_check_rule.ProductCheckRule.is_images_exceed_max_size
        ],product_data=data, image=image)

        if image in ['null', None, '', 'undefined']:
            pass
        elif image =='._no_image':
            data['image'] = settings.GOOGLE_STORAGE_STATIC_DIR+models.product.product.IMAGE_NULL
        elif image:
            image_name = image.name.replace(" ","")
            image_dir = f'user_subscription/{user_subscription.id}/product/{product.id}'
            image_url = lib.util.storage.upload_image(image_dir, image_name, image)
            data['image'] = image_url

        serializer=models.product.product.ProductSerializerUpdate(product, data=data, partial=True) 
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        product = serializer.save()

        return Response(models.product.product.ProductSerializer(product).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PUT'], url_path=r'bulk/update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def bulk_update_product(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        categories, product_status, stock_id_list = lib.util.getter.getdata(request,('categories', 'status', 'stock_id_list'), required=False)

        product_category_dict = {str(product_category.id):product_category for product_category in user_subscription.product_categories.all()}
        for stock_id in stock_id_list:
            try:
                stock = models.product.product.Product.objects.get(id=stock_id)
                if product_status in models.product.product.STATUS_CHOICES:
                    stock.status = product_status 
                if categories == [] or all(category in product_category_dict for category in categories):
                    stock.categories = categories
                stock.save()
            except Exception:
                continue
        return Response({'message': 'success'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_product(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product = lib.util.verify.Verify.get_product_from_user_subscription(user_subscription, pk)

        product.delete()
        return Response({"message": "delete success"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'copy', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def copy_product(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product = lib.util.verify.Verify.get_product_from_user_subscription(user_subscription, pk)

        copy_product = models.product.product.Product.objects.create(
            user_subscription=user_subscription,
            qty=product.qty,
            name=f'copy - {product.name}',
            description=product.description,
            price=product.price,
            image=product.image,
            status=product.status,
            categories = product.categories            
        )
        data = models.product.product.ProductSerializer(copy_product).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'(?P<product_id>[^/.]+)/wish_list/email/send', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def send_email_to_buyer_in_wish_list(self, request, product_id):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        product = lib.util.verify.Verify.get_product_from_user_subscription(user_subscription, product_id)

        for email, buyer_info in product.meta.get('wish_list',{}).items():
            title = ""
            #send email or do something #TODO
            # content = lib.helper.order_helper.OrderHelper.get_checkout_email_content(product,email)
            # jobs.send_email_job.send_email_job(title, email, content=content)
            jobs.send_email_job.send_email_job(
                lib.i18n.email.notify_wishlist_email.i18n_get_notify_wishlist_subject(lang=api_user.lang),
                email, 
                'email_notify_wishlist.html', 
                parameters={"product_name":product, "seller":api_user, "image_path":product.image,
                            "buyer_name":buyer_info.get('name','') if type(buyer_info) == dict else ''}, 
                lang=api_user.lang)
            
        
        product.meta['wish_list'] = {} 
        product.save()
        
        return Response("OK", status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['POST'], url_path=r'import', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def seller_import_product(self, request):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        file, = lib.util.getter.getdata(request,('file', ), required=True)

        product_import_processor_class:factory.product_import.default.DefaultProductImportProcessor \
            = factory.product_import.get_product_import_processor_class(user_subscription)
        product_import_processor = product_import_processor_class(user_subscription)
        product_import_processor.process(file)

        return Response("OK", status=status.HTTP_200_OK)



    #----------------------------------------------------------------for buyer-------------------------------------------------------------------------
    @action(detail=False, methods=['POST'], url_path=r'(?P<product_id>[^/.]+)/wish_list/add', permission_classes=(),  authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def wish_list_add(self, request, product_id):

        email,name, = lib.util.getter.getdata(request,('email','name',),required=True)
        product = lib.util.verify.Verify.get_product_by_id(product_id)
        
        if "wish_list" in product.meta:
            #重複add email update name
            product.meta['wish_list'][email]={'name':name}
        else:
            product.meta['wish_list'] = {email:{'name':name}}
        
        product.save()
        return Response(models.product.product.ProductSerializer(product).data, status=status.HTTP_200_OK)
    
    