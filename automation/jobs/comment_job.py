
from backend.campaign.campaign_comment.comment_processor import RQCommentProcessor
from api.models.campaign.campaign_comment import CampaignComment
from api.models.campaign.campaign import Campaign

from backend.pymongo.mongodb import db,client
from datetime import datetime

def comment_job(data):
    print(data)
    


# def comment_job(campaign_id, campaign_comment_id, order_codes_mapping):


#     campaign=Campaign.objects.get(id=campaign_id)
#     campaign_comment=CampaignComment.objects.get(id=campaign_comment_id)
#     result = RQCommentProcessor(
#                     campaign,
#                     campaign_comment,
#                     order_codes_mapping,
#                     enable_order_code=True,
#                     response_platforms=['facebook', 'youtube']
#                 ).process()