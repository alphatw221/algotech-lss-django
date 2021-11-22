from abc import ABC, abstractmethod

from backend.cart.cart_product.request import (CartProductRequest,
                                               CartProductRequestItem,
                                               RequestState)


class CartProductRequestResponder(ABC):
    @staticmethod
    @abstractmethod
    def process(request: CartProductRequest):
        ...


class CartProductRequestResponderRegular(CartProductRequestResponder):
    @staticmethod
    def process(request: CartProductRequest):
        print(request)
