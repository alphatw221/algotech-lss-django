import random
from dataclasses import dataclass

from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_product import CampaignProduct
from api.utils.orm import campaign_lucky_draw
from backend.campaign.campaign_lucky_draw.event import CampaignLuckyDrawEvent


class CampaignLuckyDrawManager:
    @staticmethod
    def process(campagin: Campaign, event: CampaignLuckyDrawEvent,
                prize_campaign_product: CampaignProduct, num_of_winner: int):
        lucky_draw = CampaignLuckyDrawProcessor(campagin, event,
                                                prize_campaign_product, num_of_winner)
        return lucky_draw.process()


@dataclass
class CampaignLuckyDrawProcessor:
    campagin: Campaign
    event: CampaignLuckyDrawEvent
    prize_campaign_product: CampaignProduct
    num_of_winner: int

    def process(self):
        candidate_set = self.event.get_candidate_set()
        try:
            if self.num_of_winner > len(candidate_set):
                self.num_of_winner = len(candidate_set)
            winner_list = random.sample(candidate_set, self.num_of_winner)
        except:
            winner_list = []

        return campaign_lucky_draw.create_campaign_lucky_draw(
            campaign=self.campagin,
            prize_campaign_product=self.prize_campaign_product,
            source_id=self.event.get_source_id(),
            source_type=self.event.get_source_type(),
            condition=self.event.get_condition(),
            condition_type=self.event.get_condition_type(),
            num_of_winner=self.num_of_winner,
            candidate_list=list(candidate_set),
            winner_list=winner_list)
