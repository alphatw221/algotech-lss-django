from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from ..models.order_product import OrderProduct, OrderProductSerializer


class OrderProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = OrderProduct.objects.all().order_by('id')
    serializer_class = OrderProductSerializer
    filterset_fields = []
