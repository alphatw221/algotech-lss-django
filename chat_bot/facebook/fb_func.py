from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from api.models.facebook.facebook_page import FacebookPage 
from api.models.auto_response.auto_response import AutoResponse
import pendulum, re

from api.models.facebook.facebook_page import FacebookPage
from backend.pymongo.mongodb import db
from datetime import datetime
from backend.api.facebook.chat_bot import api_fb_post_page_message_chat_bot


def get_auto_response(fb_id, message):
    message_list = message.lower().split(' ')
    output_msg_list = []
    output_datas = db.api_auto_response.find({'facebook_page_id': fb_id, 'input_msg': {'$in': message_list}})
    for output_data in output_datas:
        output_msg_list.append(output_data['output_msg'])
    # output_msg = AutoResponse.objects.get(facebook_page_id = fb_id, input_msg = message).output_msg
    return output_msg_list


def handleTextMessage(page_id, sender_id, message):
    try:
        fb_id = FacebookPage.objects.get(page_id = page_id).id
        campaign_id_list = []
        try:
           # campaign_id = Campaign.objects.filter(
           #     facebook_page_id = fb_id,
           #     start_at__lt = pendulum.now(),
           #     end_at__gt = pendulum.now(),
           # ).latest('start_at').id
            campaign_datas = db.api_campaign.find({'facebook_page_id': fb_id, 'start_at': {'$lt': datetime.now()}, 'end_at': {'$gt': datetime.now()}})
            for campaign_data in campaign_datas:
                campaign_id_list.append(campaign_data['id'])
        except Exception:
            campaign_id_list.append(-1)
        comment_count = db.api_campaign_comment.find({'campaign_id':{'$in': campaign_id_list}, 'customer_id': sender_id, 'platform': 'facebook'}).count()
        #comment_count = CampaignComment.objects.filter(
        #    campaign_id = campaign_id,
        #    customer_id = sender_id,
        #    platform = 'facebook'
        #).count()

        if comment_count > 0:
            output_msg_list = get_auto_response(fb_id, message['text'])
            page_token = FacebookPage.objects.get(page_id = page_id).token
            for output_msg in output_msg_list:
                response = {'text': output_msg}
                api_fb_post_page_message_chat_bot(page_token, sender_id, response)
        else:
            print ('user not commented before')

    except Exception:
        return -1
