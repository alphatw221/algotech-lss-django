from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.campaign.campaign import Campaign

from api.models.order.order import Order, OrderSerializer
from api.models.order.pre_order import PreOrder, PreOrderSerializer
from api.models.order.order_product import OrderProduct, OrderProductSerializer

from rest_framework.response import Response
from rest_framework.decorators import action
from api.utils.common.verify import Verify
from api.utils.common.verify import ApiVerifyError


class OrderProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = OrderProduct.objects.all().order_by('id')
    serializer_class = OrderProductSerializer
    filterset_fields = []
