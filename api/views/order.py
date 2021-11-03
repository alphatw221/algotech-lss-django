from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from ..models.order import Order, OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all().order_by('id')
    serializer_class = OrderSerializer
    # filterset_fields = []