from api.utils.orm.campaign import (get_active_campaign_now,
                                    get_ordering_campaign_now)


class CampaignManager:
    @staticmethod
    def get_active_campaigns():
        return get_active_campaign_now()

    @staticmethod
    def get_ordering_campaigns():
        return get_ordering_campaign_now()
