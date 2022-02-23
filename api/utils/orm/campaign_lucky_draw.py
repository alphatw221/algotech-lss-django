from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_lucky_draw import CampaignLuckyDraw
from api.models.campaign.campaign_product import CampaignProduct


def create_campaign_lucky_draw(campaign: Campaign,
                               prize_campaign_product: CampaignProduct,
                               source_id: int, source_type: str,
                               condition, condition_type: str,
                               num_of_winner: int, candidate_list: list,
                               winner_list: list):
    try:
        return CampaignLuckyDraw.objects.create(
            campaign=campaign,
            prize_campaign_product=prize_campaign_product,
            source_id=source_id,
            source_type=source_type,
            condition=condition,
            condition_type=condition_type,
            num_of_winner=num_of_winner,
            candidate_list=candidate_list,
            winner_list=winner_list)
    except Exception:
        ...
        import traceback
        print(traceback.format_exc())
