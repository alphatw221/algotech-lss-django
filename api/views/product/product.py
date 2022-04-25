from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from api.models.campaign.campaign_product import CampaignProduct, CampaignProductSerializer
from api.models.product.product import Product, ProductSerializer, ProductSerializerDropdown
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q

from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError
from api.utils.common.common import getdata
from api.utils.common.common import getparams

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler


class ProductPagination(PageNumberPagination):

    page_query_param = 'page'
    page_size_query_param = 'page_size'


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = []
    pagination_class = ProductPagination

    @action(detail=True, methods=['GET'], url_path=r'retrieve_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def retrieve_product(self, request, pk=None):
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        product = Verify.get_product_from_user_subscription(user_subscription, pk)

        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_product(self, request):

        api_user, key_word, product_status, order_by,  after_create= getparams(request,("key_word", "status", "order_by", "after_create",),with_user=True,seller=True)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        
        queryset = user_subscription.products.all()
        if product_status:
            queryset = queryset.filter(status=product_status)
        if key_word:
            queryset = queryset.filter(Q(name__icontains=key_word)|Q(tag__contains=key_word))
        if order_by:
            queryset = queryset.order_by("-"+order_by)
        if after_create:
            queryset = queryset.filter(created_at__gte=after_create)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path=r'create_product', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @api_error_handler
    def create_product(self, request):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        text = request.data['text']
        data = json.loads(text)
        data['user_subscription'] = user_subscription.id
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

        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update_product', parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_product(self, request, pk=None):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        product = Verify.get_product_from_user_subscription(user_subscription,pk)

        text = request.data['text']
        data = json.loads(text)

        image = request.data.get('image',None)
        if image:
            image_path = default_storage.save(
                f'{user_subscription.id}/product/{product.id}/{image.name}', ContentFile(image.read()))
            data['image'] = image_path
        # else:
        #     data['image'] = ""
            
        serializer = ProductSerializer(
            product, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def delete_product(self, request, pk=None):
        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        product = Verify.get_product_from_user_subscription(user_subscription,pk)

        # TODO put it into private bucket
        # if product.image:
        #     default_storage.delete(product.image)
        product.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)

    # @action(detail=False, methods=['DELETE'], url_path=r'delete_multiple_product', permission_classes=(IsAuthenticated,))
    # @api_error_handler
    # def delete_product(self, request, pk=None):
    #     # platform_id = request.query_params.get('platform_id')
    #     # platform_name = request.query_params.get('platform_name')
    #     # api_user = request.user.api_users.get(type='user')

    #     # _, _ = verify_request(
    #     #     api_user, platform_name, platform_id)
        
    #     api_user = Verify.get_seller_user(request)
    #     user_subscription = Verify.get_user_subscription_from_api_user(api_user)
    #     # product = Verify.get_product_from_user_subscription(user_subscription,pk)

    #     product_list = request.data['product_list']
    #     db.api_product.update_many({'id': {'$in': product_list}}, {'$set': {'status': 'archived'}})

    #     return Response({"message": "delete multiple products success"}, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['GET'], url_path=r'update_product_to_campaign', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_product_to_campaign(self, request, pk=None):
        
        api_user, campaign_id , order_code , max_order_amount, qty_for_sale, customer_removable , customer_editable  = getparams(
            request,
            (
                "campaign_id", 
                "order_code", 
                "max_order_amount", 
                "qty_for_sale", 
                "customer_removable", 
                "customer_editable" 
            ), with_user=True, seller=True)

        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        campaign = Verify.get_campaign_from_user_subscription(user_subscription, campaign_id)
        product = Verify.get_product_from_user_subscription(user_subscription,  pk)

        campaign_product = CampaignProduct.objects.create(
            campaign=campaign, 
            created_by=api_user, 
            product=product,
            qty_for_sale=int(qty_for_sale),
            name = product.name,
            price = product.price,
            image = product.image,
            order_code = order_code,
            max_order_amount = max_order_amount,
            type = product.type,
            customer_removable = True if int(customer_removable) else False,
            customer_editable =  True if int(customer_editable) else False
            )

        return Response(CampaignProductSerializer(campaign_product).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path=r'archive_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def archive_product(self, request, pk=None):
        # platform_id = request.query_params.get('platform_id')
        # platform_name = request.query_params.get('platform_name')
        # api_user = request.user.api_users.get(type='user')

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        product = Verify.get_product_from_user_subscription(user_subscription,pk)

        product.status="archived"
        product.save()

        return Response({"message": "product archive success"}, status=status.HTTP_200_OK)

        data = request.data

        # _, _, product = verify_request(
        #     api_user, platform_name, platform_id, product_id=pk)

        serializer = ProductSerializer(
            product, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response({"message": "product archive success"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path=r'update_image',  parser_classes=(MultiPartParser,), permission_classes=(IsAuthenticated,))
    @api_error_handler
    def update_image(self, request, pk=None):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        product = Verify.get_product_from_user_subscription(user_subscription,pk)

        if 'image' in request.data:
            image = request.data['image']
            image_path = default_storage.save(
                f'{user_subscription.id}/product/{product.id}/{image.name}', ContentFile(image.read()))
            product.image = image_path
            product.save()

        return Response(product.image, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'product_dropdown', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def product_dropdown(self, request):

        api_user = Verify.get_seller_user(request)
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)

        products = user_subscription.products.filter(
            status='enabled').all()
        serializer = ProductSerializerDropdown(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
