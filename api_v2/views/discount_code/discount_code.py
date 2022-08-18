from functools import partial
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from api import models
import lib

class DiscountCodePagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'

class DiscountCodeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.discount_code.discount_code.DiscountCode.objects.none()
    pagination_class = DiscountCodePagination
    
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

        auto_responses = user_subscription.auto_responses.all().order_by("-created_at")
        page = self.paginate_queryset(auto_responses)
        serializer = models.discount_code.discount_code.DiscountCodeSerializer(page, many=True)

        return Response(self.get_paginated_response(serializer.data).data, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'], url_path=r'create', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def create_discount_code(self, request):

        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        type, limitation = lib.util.getter.getdata(request, ("type", "limitation"), required=True)
        type_data, limitation_data = lib.util.getter.getdata(request, ("type_data", "limitation_data"), required=False)

        #TODO validation type and limitation

        serializer = models.discount_code.discount_code.DiscountCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        discount_code = serializer.save()
        
        discount_code.user_subscription = user_subscription
        discount_code.type = type
        discount_code.limitation = limitation
        discount_code.meta[type] = type_data
        discount_code.meta[limitation] = limitation_data
        discount_code.save()

        return Response(models.discount_code.discount_code.DiscountCodeSerializer(discount_code).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path=r'update', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def update_discount_code(self, request, pk=None):

        type, limitation = lib.util.getter.getdata(request, ("type", "limitation"), required=True)
        type_data, limitation_data = lib.util.getter.getdata(request, ("type_data", "limitation_data"), required=False)


        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        discount_code = lib.util.verify.Verify.get_discount_code_from_user_subscription(user_subscription, pk)

        serializer = models.discount_code.discount_code.DiscountCodeSerializer(discount_code, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        discount_code = serializer.save()

        discount_code.type = type
        discount_code.limitation = limitation
        discount_code.meta[type] = type_data
        discount_code.meta[limitation] = limitation_data
        discount_code.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['DELETE'], url_path=r'delete', permission_classes=(IsAuthenticated,))
    @lib.error_handle.error_handler.api_error_handler.api_error_handler
    def delete_discount_code(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_seller_user(request)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        discount_code = lib.util.verify.Verify.get_discount_code_from_user_subscription(user_subscription, pk)

        discount_code.delete()

        return Response({"message": "delete success"}, status=status.HTTP_200_OK)

