from functools import partial
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from api import models
import lib

from datetime import datetime


class DiscountCodePagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'

class DiscountCodeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = models.discount_code.discount_code.DiscountCode.objects.none()
    pagination_class = DiscountCodePagination
    

    #-----------------------------------------------buyer----------------------------------
    @action(detail=False, methods=['GET'], url_path=r'list/(?P<cart_oid>[^/.]+)', permission_classes=(), authentication_classes=[])
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def buyer_list_discount_code(self, request, cart_oid):
        
        _type, = lib.util.getter.getparams(request,('type',),with_user=False)

        cart = lib.util.verify.Verify.get_cart_with_oid(cart_oid)
        campaign = cart.campaign
        user_subscription = campaign.user_subscription

        queryset = user_subscription.discount_codes.filter(start_at__lte=datetime.utcnow(), end_at__gte=datetime.utcnow())

        if _type in models.discount_code.discount_code.TYPE_CHOICES:
            queryset = queryset.filter(type=_type)
        data = models.discount_code.discount_code.DiscountCodeSerializer(queryset, many=True).data
        # print(data)
        return Response(data, status=status.HTTP_200_OK)

    #-----------------------------------------------seller----------------------------------
    @action(detail=True, methods=['GET'], url_path=r'retrieve', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def retrieve_discount_code(self, request, pk=None):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        discount_code = lib.util.verify.Verify.get_discount_code_from_user_subscription(user_subscription, pk)

        return Response(models.discount_code.discount_code.DiscountCodeSerializer(discount_code).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path=r'list', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def list_discount_code(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        discount_codes = user_subscription.discount_codes.all().order_by("-created_at")
        page = self.paginate_queryset(discount_codes)
        serializer = models.discount_code.discount_code.DiscountCodeSerializer(page, many=True)

        return Response(self.get_paginated_response(serializer.data).data, status=status.HTTP_200_OK)


    

    @action(detail=False, methods=['POST'], url_path=r'create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_discount_code(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        # type, limitations = lib.util.getter.getdata(request, ("type", "limitations"), required=True)


        #TODO validation type and limitations
        # print(request.data)
        serializer = models.discount_code.discount_code.DiscountCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            discount_code = serializer.save()
            
            discount_code.user_subscription = user_subscription
            
            discount_code.save()
        except Exception :      
            raise lib.error_handle.error.api_error.ApiVerifyError('duplicate_discount_code')

        return Response(models.discount_code.discount_code.DiscountCodeSerializer(discount_code).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_discount_code(self, request, pk=None):

        # type, limitations = lib.util.getter.getdata(request, ("type", "limitations"), required=True)

        #TODO validation type and limitations

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        discount_code = lib.util.verify.Verify.get_discount_code_from_user_subscription(user_subscription, pk)

        serializer = models.discount_code.discount_code.DiscountCodeSerializer(discount_code, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            discount_code = serializer.save()
        except Exception :
            raise lib.error_handle.error.api_error.ApiVerifyError('duplicate_discount_code')
        

        return Response(models.discount_code.discount_code.DiscountCodeSerializer(discount_code).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_discount_code(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        discount_code = lib.util.verify.Verify.get_discount_code_from_user_subscription(user_subscription, pk)

        discount_code.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)

