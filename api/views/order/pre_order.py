from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.order.pre_order import PreOrder, PreOrderSerializer


class PreOrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = PreOrder.objects.all().order_by('id')
    serializer_class = PreOrderSerializer
    filterset_fields = []
