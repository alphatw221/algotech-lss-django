
import pendulum
from api.models.campaign.campaign_product import CampaignProduct
from backend.campaign.campaign.announcer import (CampaignAnnouncer,
                                                 CampaignAnnouncerError)
from backend.campaign.campaign_product.manager import (AlreadyInUseError,
                                                       CampaignProductManager)


class CampaignProductStatusProcessor:
    @staticmethod
    def update_status(campaign_product: CampaignProduct, status: int):
        try:
            campaign_product = CampaignProductManager.update_status(
                campaign_product, status)
        except AlreadyInUseError as e:
            raise e

        try:
            if status == 0:
                result = CampaignAnnouncer.announce_campaign_product_deactivate(
                    campaign_product)
            elif status == 1:
                result = CampaignAnnouncer.announce_campaign_product_activate(
                    campaign_product)
        except CampaignAnnouncerError as e:
            raise e
        
        campaign_product.meta.setdefault('status_history', []).append({
            'time': pendulum.now('UTC'),
            'status': status,
            'response_result': result
        })
        campaign_product.save()

        return campaign_product
