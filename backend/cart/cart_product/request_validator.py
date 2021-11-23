from abc import ABC

from backend.cart.cart_product.manager import CartProductManager
from backend.cart.cart_product.request import CartProductRequest, RequestState


class CartProductRequestValidator(ABC):
    def process():
        ...


class CartProductRequestValidatorRegular(CartProductRequestValidator):
    def process(self, request: CartProductRequest):
        for item in request.get_items():
            if not item.campaign_product.status:
                item.state = RequestState.INVALID_PRODUCT_NOT_ACTIVATED
                return
            if item.campaign_product.max_order_amount and \
                    item.qty > item.campaign_product.max_order_amount:
                item.state = RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT
                return

            existing_cart_product = CartProductManager.get_last_valid_cart_product(
                request.campaign_comment.campaign,
                item.campaign_product,
                request.campaign_comment.customer_id,
            )
            if not existing_cart_product:
                if item.qty == 0:
                    item.state = RequestState.INVALID_ADD_ZERO_QTY
                else:
                    item.state = RequestState.ADDING
            else:
                item.orig_cart_product = existing_cart_product
                if item.qty > 0:
                    if not item.campaign_product.customer_editable:
                        item.state = RequestState.INVALID_EDIT_NOT_ALLOWED
                    else:
                        item.state = RequestState.UPDATING
                elif item.qty == 0:
                    if not item.campaign_product.customer_removable:
                        item.state = RequestState.INVALID_REMOVE_NOT_ALLOWED
                    else:
                        item.state = RequestState.DELETING
                else:
                    item.state = RequestState.INVALID_UNKNOWN_REQUEST


class CartProductRequestValidatorAllValid(CartProductRequestValidator):
    def process(self, request: CartProductRequest):
        for item in request.get_items():
            existing_cart_product = CartProductManager.get_last_valid_cart_product(
                request.campaign_comment.campaign,
                item.campaign_product,
                request.campaign_comment.customer_id,
            )
            if not existing_cart_product:
                item.state = RequestState.ADDING
            else:
                item.orig_cart_product = existing_cart_product
                if item.qty > 0:
                    item.state = RequestState.UPDATING
                elif item.qty == 0:
                    item.state = RequestState.DELETING
                else:
                    item.state = RequestState.INVALID_UNKNOWN_REQUEST
