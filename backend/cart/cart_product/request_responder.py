from abc import ABC

from backend.cart.cart_product.request import (CartProductRequest,
                                               CartProductRequestItem,
                                               RequestState)


class CartProductRequestResponder(ABC):
    def process(self, request: CartProductRequest):
        ...


class CartProductRequestResponderRegular(CartProductRequestResponder):
    def process(self, request: CartProductRequest):
        print(request)
