from enum import Enum, auto

import pendulum
from api.models.campaign.campaign_product import CampaignProduct
from backend.campaign.campaign.announcer import (CampaignAnnouncer,
                                                 CampaignAnnouncerError)
from backend.campaign.campaign_product.manager import (AlreadyInUseError,
                                                       CampaignProductManager)


class InvalidEventError(Exception):
    """Error when setting invalid event."""


class CampaignProductStatusProcessor:
    class Event(Enum):
        DEACTIVATE = auto()
        ACTIVATE = auto()
        SOLD_OUT = auto()

    @staticmethod
    def update_status(campaign_product: CampaignProduct, event: Event):
        if event == CampaignProductStatusProcessor.Event.DEACTIVATE:
            to_status = 0
            to_announce = CampaignAnnouncer.announce_campaign_product_deactivate
        elif event == CampaignProductStatusProcessor.Event.ACTIVATE:
            to_status = 1
            to_announce = CampaignAnnouncer.announce_campaign_product_activate
        elif event == CampaignProductStatusProcessor.Event.SOLD_OUT:
            to_status = 0
            to_announce = CampaignAnnouncer.announce_campaign_product_sold_out
        else:
            raise InvalidEventError()

        try:
            campaign_product = CampaignProductManager.update_status(
                campaign_product, to_status)
            response_result = to_announce(campaign_product)
        except AlreadyInUseError:
            raise
        except CampaignAnnouncerError:
            raise

        campaign_product.meta.setdefault('status_history', []).append({
            'time': pendulum.now('UTC'),
            'event': event.name,
            'status': to_status,
            'response_result': response_result
        })
        campaign_product.save()

        return campaign_product

    @staticmethod
    def get_campaign_product_sold_out_task(campaign_product: CampaignProduct):
        def _campaign_product_sold_out_task(campaign_product: CampaignProduct):
            try:
                CampaignProductStatusProcessor.update_status(campaign_product,
                                                             CampaignProductStatusProcessor.Event.SOLD_OUT)
            except Exception:
                ...

        return _campaign_product_sold_out_task(campaign_product)
