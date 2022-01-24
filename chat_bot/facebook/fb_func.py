from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from api.models.facebook.facebook_page import FacebookPage 
from api.models.auto_response.auto_response import AutoResponse
import pendulum, re

from api.models.facebook.facebook_page import FacebookPage
from backend.pymongo.mongodb import db
from backend.api.facebook.chat_bot import api_fb_post_page_message_chat_bot


def get_auto_response(fb_id, message):
    message_list = message.split(' ')
    output_msg = db.api_auto_reply.find_one({'facebook_page_id': fb_id, 'input_msg': {'$in': message_list}})['output_msg']
    # output_msg = AutoResponse.objects.get(facebook_page_id = fb_id, input_msg = message).output_msg
    return output_msg


def handleTextMessage(page_id, sender_id, message):
    try:
        fb_id = FacebookPage.objects.get(page_id = page_id).id
        
        try:
            campaign_id = Campaign.objects.filter(
                facebook_page_id = fb_id,
                ordering_start_at__lt = pendulum.now(),
                end_at__gt = pendulum.now(),
            ).latest('start_at').id
        except Exception:
            campaign_id = -1
        
        comment_count = CampaignComment.objects.filter(
            campaign_id = campaign_id,
            customer_id = sender_id,
            platform = 'facebook'
        ).count()

        if comment_count > 0:
            outout_msg = get_auto_response(fb_id, message['text'])
            page_token = FacebookPage.objects.get(page_id = page_id).token
            response = {'text': outout_msg}
            api_fb_post_page_message_chat_bot(page_token, sender_id, response)
        else:
            print ('user not commented before')

    except Exception:
        return -1