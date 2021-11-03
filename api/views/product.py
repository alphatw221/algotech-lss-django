from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from ..models.product import Product, ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    filterset_fields = []
