from dataclasses import dataclass
from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_product import CampaignProduct


@dataclass
class CartProductRequestItem:
    campaign_product: CampaignProduct
    qty: int
    order_code: str


@dataclass
class CartProductRequest:
    campaign_comment: CampaignComment

    def __post_init__(self):
        self.items: list[CartProductRequestItem] = []

    def __repr__(self) -> str:
        return f'CartProductRequest({self.campaign_comment.id=} {self.items})'

    def add_item(self, campaign_product: CampaignProduct,
                 qty: int, order_code: str):
        try:
            self.items.append(
                CartProductRequestItem(campaign_product, qty, order_code)
            )
        except:
            return

    def get_items(self):
        return self.items
