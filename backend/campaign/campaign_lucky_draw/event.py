from abc import ABC, abstractmethod
from dataclasses import dataclass

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.utils.orm import cart_product


@dataclass
class CampaignLuckyDrawEvent(ABC):
    @abstractmethod
    def get_source_id(self):
        ...

    @abstractmethod
    def get_source_type(self):
        ...

    @abstractmethod
    def get_condition(self):
        ...

    @abstractmethod
    def get_condition_type(self):
        ...

    @abstractmethod
    def get_candidate_set(self):
        ...


@dataclass
class DrawFromCartProductEvent(CampaignLuckyDrawEvent):
    campagin: Campaign
    campagin_product: CampaignProduct

    def get_source_id(self):
        return self.campagin_product.id

    def get_source_type(self):
        return 'cart_product'

    def get_condition(self):
        return None

    def get_condition_type(self):
        return 'lucky_draw_cart_products'

    def get_candidate_set(self):
        cart_products = cart_product.filter_cart_products(self.campagin, self.campagin_product,
                                                          ('order_code', 'cart'),
                                                          ('valid',))
        return {
            (cart_product.platform,
             cart_product.customer_id,
             cart_product.customer_name)
            for cart_product in cart_products
        }
