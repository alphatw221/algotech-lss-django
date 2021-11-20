from abc import ABC, abstractmethod
from backend.cart.cart_product.request import CartProductRequest, CartProductRequestItem, RequestState
from api.utils.orm.cart_product import update_or_create_cart_product


class CartProductRequestProcessor(ABC):
    @staticmethod
    @abstractmethod
    def process(request: CartProductRequest):
        ...


class CartProductRequestProcessorV1(CartProductRequestProcessor):
    @staticmethod
    def process(request: CartProductRequest):
        for item in request.get_items():
            CartProductRequestProcessorV1._process_item_request(request, item)

    def _process_item_request(request: CartProductRequest, item: CartProductRequestItem):
        if item.state == RequestState.VALID:
            CartProductRequestProcessorV1._create_cart_product(request, item)
            item.state = RequestState.CREATED
        else:
            ...

    @staticmethod
    def _create_cart_product(request: CartProductRequest, item: CartProductRequestItem):
        update_or_create_cart_product(
            request.campaign_comment.campaign,
            item.campaign_product,
            request.campaign_comment,
            {
                'qty': item.qty,
                'order_code': item.order_code,
                'platform': request.campaign_comment.platform,
                'customer_id': request.campaign_comment.customer_id,
                'customer_name': request.campaign_comment.customer_name,
                'type': 'order_code',
                'status': 'valid',
            }
        )
