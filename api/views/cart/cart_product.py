from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.models.cart.cart_product import CartProduct, CartProductSerializer


class CartProductViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CartProduct.objects.all().order_by('id')
    serializer_class = CartProductSerializer
    filterset_fields = []
