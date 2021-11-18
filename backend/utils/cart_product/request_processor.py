from abc import ABC, abstractmethod
from api.models.cart.cart_product import CartProduct
from backend.utils.cart_product.request import CartProductRequest, CartProductRequestItem


class CartProductRequestProcessor(ABC):
    @staticmethod
    @abstractmethod
    def process(request: CartProductRequest):
        ...


class CartProductRequestProcessorV1(CartProductRequestProcessor):
    @staticmethod
    def process(request: CartProductRequest):
        for item in request.get_items():
            CartProductRequestProcessorV1._validate_request(item)
            CartProductRequestProcessorV1._create_cart_product(item)
        CartProductRequestProcessorV1._external_actions(request)

    @staticmethod
    def _validate_request(item: CartProductRequestItem):
        ...
        # TODO: check by qty and item.campaign_product

    @staticmethod
    def _create_cart_product(item: CartProductRequestItem):
        ...
        # TODO: create cart product if valid
        CartProduct.objects.all()

    @staticmethod
    def _external_actions(request):
        ...
        # TODO: request.campaign_comment.platform
