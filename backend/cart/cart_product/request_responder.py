from abc import ABC

from backend.cart.cart_product.request import (CartProductRequest,
                                               CartProductRequestItem,
                                               RequestState)


class CartProductRequestResponder(ABC):
    def process():
        ...


class CartProductRequestResponderRegular(CartProductRequestResponder):
    def process(self, request: CartProductRequest):
        print(request)
