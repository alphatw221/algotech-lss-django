import random
from dataclasses import dataclass
from enum import Enum

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.utils.orm import campaign_lucky_draw, cart_product


class UnsupportedEventError(Exception):
    """Error when choose unsupported Campaign Lucky Draw event."""


class CampaignLuckyEvent(Enum):
    DRAW_FROM_CART_PRODUCT = {
        'source_type': 'cart_product', 'condition_type': 'cart_product'}


class CampaignLuckyDrawManager:
    @staticmethod
    def process(campagin: Campaign, campgin_product: CampaignProduct,
                prize_campaign_product: CampaignProduct, num_of_winner: int,
                event: CampaignLuckyEvent):
        lucky_draw = CampaignLuckyDrawProcessor(campagin, campgin_product,
                                                prize_campaign_product, num_of_winner,
                                                event)
        return lucky_draw


@dataclass
class CampaignLuckyDrawProcessor:
    campagin: Campaign
    campgin_product: CampaignProduct
    prize_campaign_product: CampaignProduct
    num_of_winner: int
    event: CampaignLuckyEvent

    def process(self):
        if self.event == CampaignLuckyEvent.DRAW_FROM_CART_PRODUCT:
            candidate_set = self._get_campaign_cart_candidate_set()
            source_id = self.campgin_product.id
            condition = None
        else:
            raise UnsupportedEventError()

        try:
            if self.num_of_winner > len(candidate_set):
                self.num_of_winner = len(candidate_set)
            winner_list = random.sample(candidate_set, self.num_of_winner)
        except:
            winner_list = []
        print(winner_list)

        return campaign_lucky_draw.create_campaign_lucky_draw(
            campaign=self.campagin,
            prize_campaign_product=self.prize_campaign_product,
            source_id=source_id,
            source_type=self.event.value['source_type'],
            condition=condition,
            condition_type=self.event.value['condition_type'],
            num_of_winner=self.num_of_winner,
            candidate_list=list(candidate_set),
            winner_list=winner_list)

    def _get_campaign_cart_candidate_set(self):
        cart_products = cart_product.filter_cart_products(self.campagin, self.campgin_product,
                                                          ('order_code', 'cart'),
                                                          ('valid',))
        return {
            (cart_product.platform, cart_product.customer_id)
            for cart_product in cart_products
        }
