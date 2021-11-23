from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from api.models import order, product
from api.models.product.product import Product, ProductSerializer
from rest_framework.decorators import action


class ProductPagination(PageNumberPagination):

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


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = []
    pagination_class = ProductPagination

    @action(detail=False, methods=['GET'], url_path=r'user_products')
    def get_user_products(self, request):

        order_by = request.query_params.get('order_by')
        product_status = request.query_params.get('status')
        key_word = request.query_params.get('key_word')

        api_user = request.user.api_users.get(type='user')
        # TODO 檢查
        if not api_user:
            return Response({"message": "no user found"}, status=status.HTTP_400_BAD_REQUEST)
        elif api_user.status != "valid":
            return Response({"message": "not activated user"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Product.objects.all()
        try:
            if product_status:
                queryset = queryset.filter(status=product_status)
            if key_word:
                queryset = queryset.filter(name__icontains=key_word)
            if order_by:
                queryset = queryset.order_by(order_by)
        except:
            return Response({"message": "query error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(queryset, status=status.HTTP_200_OK)
