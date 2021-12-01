from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.utils.orm import cart_product


class CampaignLuckyDrawEvent(ABC):
    ...


@dataclass
class DrawFromCartProductEvent(ABC):
    campagin: Campaign
    campagin_product: CampaignProduct

    def get_source_id(self):
        return self.campagin_product.id

    def get_source_type(self):
        return 'cart_product'

    def get_condition(self):
        return None

    def get_condition_type(self):
        return 'cart_product'

    def get_candidate_set(self):
        cart_products = cart_product.filter_cart_products(self.campagin, self.campagin_product,
                                                          ('order_code', 'cart'),
                                                          ('valid',))
        return {
            (cart_product.platform, cart_product.customer_id)
            for cart_product in cart_products
        }
