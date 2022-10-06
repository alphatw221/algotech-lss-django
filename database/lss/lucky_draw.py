from ._config import db
from ._config import Collection

__collection = db.api_campaign_lucky_draw


class CampaignLuckyDraw(Collection):

    _collection = db.api_campaign_lucky_draw
    collection_name='api_campaign_lucky_draw'
    