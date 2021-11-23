from abc import ABC
from dataclasses import dataclass

from backend.campaign.campaign_product.manager import (
    CampaignProductManager, InsufficientInventoryError, NegativeQtyError)
from backend.cart.cart_product.manager import CartProductManager
from backend.cart.cart_product.request import (CartProductRequest,
                                               CartProductRequestItem,
                                               RequestState)


@dataclass
class CartProductRequestProcessor(ABC):
    def process():
        ...


@dataclass
class CartProductRequestProcessorRegular(CartProductRequestProcessor):
    check_inv: bool = True

    def process(self, request: CartProductRequest):
        for item in request.get_items():
            self._process_item_request(request, item)

    def _process_item_request(self, request: CartProductRequest, item: CartProductRequestItem):
        try:
            if item.state == RequestState.ADDING:
                self._add_cart_product(request, item)
                item.state = RequestState.ADDED
            elif item.state == RequestState.UPDATING:
                self._update_cart_product(item)
                item.state = RequestState.UPDATED
            elif item.state == RequestState.DELETING:
                self._delete_cart_product(item)
                item.state = RequestState.DELETED
        except InsufficientInventoryError:
            item.state = RequestState.INSUFFICIENT_INV
        except NegativeQtyError:
            item.state = RequestState.INVALID_NEGATIVE_QTY

    def _add_cart_product(self, request: CartProductRequest, item: CartProductRequestItem):
        self._update_qty_sold(item.campaign_product,
                              item.qty)
        CartProductManager.update_or_create_cart_product(
            request.campaign_comment.campaign,
            item.campaign_product,
            request.campaign_comment,
            item.qty,
            item.campaign_product.order_code,
            request.campaign_comment.platform,
            request.campaign_comment.customer_id,
            request.campaign_comment.customer_name,
            'order_code',
            'valid',
        )

    def _update_cart_product(self, item: CartProductRequestItem):
        self._update_qty_sold(item.campaign_product,
                              item.qty, item.orig_cart_product.qty)
        CartProductManager.update_cart_product_qty(
            item.orig_cart_product, item.qty)

    def _delete_cart_product(self, item: CartProductRequestItem):
        self._update_qty_sold(item.campaign_product,
                              0, item.orig_cart_product.qty)
        CartProductManager.update_cart_product_qty(
            item.orig_cart_product, 0)

    def _update_qty_sold(self, *args, **kwargs):
        return CampaignProductManager.update_qty_sold(
            *args, **kwargs, check_inv=self.check_inv)
