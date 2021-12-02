from abc import ABC, abstractmethod
from dataclasses import dataclass

from backend.campaign.campaign_product.manager import (
    CampaignProductManager, InsufficientInventoryError, NegativeQtyError)
from backend.cart.cart_product.manager import CartProductManager
from backend.cart.cart_product.request import (CartProductRequest,
                                               CartProductRequestItem,
                                               RequestState)


@dataclass
class CartProductRequestProcessor(ABC):
    @abstractmethod
    def process():
        ...

    def _update_qty_sold(self, *args, **kwargs):
        return CampaignProductManager.update_qty_sold(
            *args, **kwargs, check_inv=self.check_inv)


@dataclass
class CartProductRequestProcessorStandard(CartProductRequestProcessor):
    check_inv: bool = True
    cart_product_type: str = 'n/a'

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
            request.campaign,
            item.campaign_product,
            request.campaign_comment,
            item.qty,
            item.campaign_product.order_code,
            request.platform,
            request.customer_id,
            request.customer_name,
            self.cart_product_type,
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


@dataclass
class CartProductRequestProcessorLuckyDraw(CartProductRequestProcessor):
    check_inv: bool = True
    cart_product_type: str = 'n/a'

    def process(self, request: CartProductRequest):
        for item in request.get_items():
            self._process_item_request(request, item)

    def _process_item_request(self, request: CartProductRequest, item: CartProductRequestItem):
        try:
            if item.state == RequestState.ADDING:
                self._add_cart_product(request, item)
                item.state = RequestState.ADDED
        except InsufficientInventoryError:
            item.state = RequestState.INSUFFICIENT_INV
        except NegativeQtyError:
            item.state = RequestState.INVALID_NEGATIVE_QTY

    def _add_cart_product(self, request: CartProductRequest, item: CartProductRequestItem):
        self._update_qty_sold(item.campaign_product,
                              item.qty)
        CartProductManager.create_cart_product(
            request.campaign,
            item.campaign_product,
            request.campaign_comment,
            item.qty,
            None,
            request.platform,
            request.customer_id,
            request.customer_name,
            self.cart_product_type,
            'valid'
        )
