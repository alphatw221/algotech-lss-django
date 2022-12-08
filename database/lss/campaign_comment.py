from ._config import db
from ._config import Collection
from api import models
__collection = db.api_campaign_comment


class CampaignComment(Collection):

    _collection = db.api_campaign_comment
    collection_name='api_campaign_comment'
    template = models.campaign.campaign_comment.api_campaign_comment_template

    @classmethod
    def get_latest_comment_object(cls, campaign_id, platform_name):
        data = cls._collection.find_one(
            {'platform':platform_name, 'campaign_id': campaign_id}, sort=[('created_time', -1)])
        if data:
            return cls(data.get('id'), data.get('_id'), data)

def get_count_in_campaign(campaign_id):
    if campaign_id:
        return __collection.find({'campaign_id': campaign_id}).count()
    return 0