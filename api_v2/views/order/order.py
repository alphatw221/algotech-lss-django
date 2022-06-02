from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes

from api import models
from api.utils.common.order_helper import PreOrderHelper
import lib

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = models.order.order.Order.objects.all().order_by('id')

    @action(detail=True, methods=['GET'], url_path=r'buyer/retrieve', permission_classes=(IsAuthenticated,))
    def buyer_retrieve_order(self, request, pk=None):
        api_user = lib.util.verify.Verify.get_customer_user(request)
        order = lib.util.verify.Verify.get_order_by_api_user(api_user, pk)

        return Response(models.order.order.OrderSerializer(order).data, status=status.HTTP_200_OK)
