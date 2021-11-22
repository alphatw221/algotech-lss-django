from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from api.models.product.product import Product, ProductSerializer


class ProductPagination(LimitOffsetPagination):

    default_limit = 25
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    filterset_fields = []
    pagination_class = ProductPagination
