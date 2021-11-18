from abc import ABC, abstractmethod
from api.models.cart.cart_product import CartProduct
from api.utils.common.cart_product.request import CartProductRequest, CartProductRequestItem


class CartProductRequestProcessor(ABC):
    @staticmethod
    @abstractmethod
    def process(request: CartProductRequest):
        ...


class CartProductRequestProcessorV1(CartProductRequestProcessor):
    @staticmethod
    def process(request: CartProductRequest):
        for item in request.get_items():
            CartProductRequestProcessorV1._create_cart_product(item)
            CartProductRequestProcessorV1._external_actions()

    @staticmethod
    def _create_cart_product(item: CartProductRequestItem):
        print(item)
        CartProduct.objects.all()

    @staticmethod
    def _external_actions():
        ...
        # TODO
