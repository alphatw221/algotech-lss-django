from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.order.order import Order, OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Order.objects.all().order_by('id')
    serializer_class = OrderSerializer
    filterset_fields = []


# retrieve

# list

# update_payment_and_delievery

# payment_complete
# ...update status
# ...update payment detail

# cancel
# ...check order status staging
