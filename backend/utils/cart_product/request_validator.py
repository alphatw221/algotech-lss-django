from abc import ABC, abstractmethod
from backend.utils.cart_product.request import CartProductRequest, CartProductRequestItem, RequestState


class CartProductRequestValidator(ABC):
    @staticmethod
    @abstractmethod
    def process(request: CartProductRequest):
        ...


class CartProductRequestValidatorV1(CartProductRequestValidator):
    @staticmethod
    def process(request: CartProductRequest):
        for item in request.get_items():
            item.state = RequestState.VALID
            # TODO: check by qty and item.campaign_product
