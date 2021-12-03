from abc import ABC, abstractmethod
from dataclasses import dataclass

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.utils.orm import campaign_comment as orm_campaign_comment
from api.utils.orm import cart_product as orm_cart_product


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
class DrawFromCartProductsEvent(CampaignLuckyDrawEvent):
    campagin: Campaign
    campagin_product: CampaignProduct

    def get_source_id(self):
        return self.campagin_product.id

    def get_source_type(self):
        return 'campagin_product'

    def get_condition(self):
        return None

    def get_condition_type(self):
        return 'lucky_draw_cart_products'

    def get_candidate_set(self):
        cart_products = orm_cart_product.filter_cart_products(
            self.campagin, self.campagin_product,
            ('order_code', 'cart'),
            ('valid',)
        )
        return {
            (cart_product.platform,
             cart_product.customer_id,
             cart_product.customer_name)
            for cart_product in cart_products
        }


@dataclass
class DrawFromCampaignCommentsEvent(ABC):
    campagin: Campaign
    keyword: str

    def get_source_id(self):
        return self.campagin.id

    def get_source_type(self):
        return 'campagin'

    def get_condition(self):
        return self.keyword

    def get_condition_type(self):
        return 'lucky_draw_campaign_comments'

    def get_candidate_set(self):
        campaign_comments = orm_campaign_comment.get_keyword_campaign_comments(
            self.campagin, self.keyword,
        )
        return {
            (campaign_comment['platform'],
             campaign_comment['customer_id'],
             campaign_comment['customer_name'])
            for campaign_comment in campaign_comments
        }


@dataclass
class DrawFromCampaignLikesEvent(ABC):
    def get_source_id(self):
        ...

    def get_source_type(self):
        return 'campaign_likes'

    def get_condition(self):
        return None

    def get_condition_type(self):
        return 'lucky_draw_campaign_likes'

    def get_candidate_set(self):
        ...
