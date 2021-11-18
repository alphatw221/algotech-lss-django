from dataclasses import dataclass
from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign_product import CampaignProduct


@dataclass
class CartProductRequest:
    campaign_product: CampaignProduct
    campaign_comment: CampaignComment
    qty: int
    order_code: str

    def __repr__(self) -> str:
        info = ', '.join([f'{self.campaign_product.id=}',
                         f'{self.campaign_comment.id=}',
                          f'{self.qty=}',
                          f'{self.order_code=}', ])
        return f'CartProductRequest({info})'


class CartProductRequestHandler:
    @staticmethod
    def place_cart_product(request: CartProductRequest):
        ...  # TODO
