from abc import ABC, abstractmethod

from backend.cart.cart_product.request import (CartProductRequest,
                                               CartProductRequestItem,
                                               RequestState)


class CartProductRequestResponder(ABC):
    @abstractmethod
    def process(self, request: CartProductRequest):
        ...


class CartProductRequestResponderRegular(CartProductRequestResponder):
    def process(self, request: CartProductRequest):
        print(request)
