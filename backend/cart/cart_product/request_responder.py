from abc import ABC, abstractmethod
from backend.cart.cart_product.request import CartProductRequest, CartProductRequestItem, RequestState


class CartProductRequestResponder(ABC):
    @staticmethod
    @abstractmethod
    def process(request: CartProductRequest):
        ...


class CartProductRequestResponderV1(CartProductRequestResponder):
    @staticmethod
    def process(request: CartProductRequest):
        ...
        # TODO: respond based on platform
