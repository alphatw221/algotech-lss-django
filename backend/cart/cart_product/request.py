from dataclasses import dataclass, field
from enum import Enum, auto

from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_product import CampaignProduct
from api.models.cart.cart_product import CartProduct


class RequestState(Enum):
    ADDING = auto()
    ADDED = auto()
    UPDATING = auto()
    UPDATED = auto()
    DELETING = auto()
    DELETED = auto()
    INSUFFICIENT_INV = auto()
    INVALID_PRODUCT_NOT_ACTIVATED = auto()
    INVALID_EXCEED_MAX_ORDER_AMOUNT = auto()
    INVALID_REMOVE_NOT_ALLOWED = auto()
    INVALID_EDIT_NOT_ALLOWED = auto()
    INVALID_NEGATIVE_QTY = auto()
    INVALID_ADD_ZERO_QTY = auto()
    INVALID_UNKNOWN_REQUEST = auto()


@dataclass
class CartProductRequestItem:
    campaign_product: CampaignProduct
    qty: int
    orig_cart_product: CartProduct = None
    state: RequestState = None

    def __repr__(self) -> str:
        return (
            f'campaign_product={self.campaign_product.id},'
            f'qty={self.qty},'
            f'state={self.state.name}'
        )


@dataclass
class CartProductRequest:
    campaign_comment: CampaignComment
    items: list[CartProductRequestItem] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f'CartProductRequest({self.campaign_comment.id=} {self.campaign_comment.campaign=} '
            f'{self.campaign_comment.message=} {self.campaign_comment.comment_id=} '
            f'{self.campaign_comment.customer_id=} {self.campaign_comment.customer_name=} '
            f'{self.items})'
        )

    def add_item(self, campaign_product: CampaignProduct, qty: int):
        try:
            self.items.append(
                CartProductRequestItem(campaign_product, qty))
        except:
            return

    def get_items(self):
        return self.items

    def get_items_repr(self):
        return f'{self.items}'
