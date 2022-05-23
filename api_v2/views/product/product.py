from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response

from api import models
from api import utils

from api.utils.error_handle.error_handler.api_error_handler import api_error_handler


class ProductPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.product.product.Product.objects.all()
    serializer_class = models.product.product.ProductSerializer
    pagination_class = ProductPagination

    @action(detail=False, methods=['GET'], url_path=r'list_product', permission_classes=(IsAuthenticated,))
    @api_error_handler
    def list_product(self, request):
        api_user, search_column, keyword = utils.common.common.getparams(request,("search_column", "keyword",),with_user=True,seller=True)
        user_subscription = utils.common.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        kwargs = {}
        if (search_column in ["", None]) and (keyword not in [None, ""]):
            raise utils.common.verify.ApiVerifyError("search_column field can not be empty when keyword has value")
        if (search_column not in ['undefined', '']) and (keyword not in ['undefined', '', None]):
            kwargs = { search_column + '__icontains': keyword }

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