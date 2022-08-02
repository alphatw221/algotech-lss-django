from api.models.campaign.campaign import Campaign
from api.models.campaign.campaign_comment import CampaignComment
from api.models.facebook.facebook_page import FacebookPage 
from api.models.auto_response.auto_response import AutoResponse
import pendulum, re

from api.models.facebook.facebook_page import FacebookPage
from api.models.instagram.instagram_profile import InstagramProfile
from backend.pymongo.mongodb import db
from datetime import datetime
from backend.api.facebook.chat_bot import api_fb_post_page_message_chat_bot

import service

def get_fb_auto_response(fb_id, message):
    message_list = [message.lower()]
    output_msg_list = []
    output_datas = db.api_auto_response.find({'facebook_page_id': fb_id, 'input_msg': {'$in': message_list}})
    for output_data in output_datas:
        output_msg_list.append(output_data['output_msg'])
    # output_msg = AutoResponse.objects.get(facebook_page_id = fb_id, input_msg = message).output_msg
    return output_msg_list

def get_ig_auto_response(ig_id, message):
    message_list = [message.lower()]
    print("message_list", message_list)
    output_msg_list = []
    output_datas = db.api_auto_response.find({'instagram_profile_id': ig_id, 'input_msg': {'$in': message_list}})
    for output_data in output_datas:
        output_msg_list.append(output_data['output_msg'])
    return output_msg_list


def handleTextMessage(object, page_id, sender_id, message):
    try:
        if object == "page":
            fb_id = FacebookPage.objects.get(page_id = page_id).id
            campaign_id_list = []
            try:
                campaign_datas = db.api_campaign.find({'facebook_page_id': fb_id, 'start_at': {'$lt': datetime.utcnow()}, 'end_at': {'$gt': datetime.utcnow()}})
                for campaign_data in campaign_datas:
                    campaign_id_list.append(campaign_data['id'])
            except Exception:
                campaign_id_list.append(-1)
            comment_count = db.api_campaign_comment.find({'campaign_id':{'$in': campaign_id_list}, 'customer_id': sender_id, 'platform': 'facebook'}).count()

            if comment_count > 0:
                output_msg_list = get_fb_auto_response(fb_id, message['text'])
                page_token = FacebookPage.objects.get(page_id = page_id).token
                for output_msg in output_msg_list:
                    response = {'text': output_msg}
                    api_fb_post_page_message_chat_bot(page_token, sender_id, response)
            else:
                print ('user not commented before')
            # output_msg_list = get_fb_auto_response(fb_id, message['text'])
            # page_token = FacebookPage.objects.get(page_id = page_id).token
            # for output_msg in output_msg_list:
            #     response = {'text': output_msg}
            #     api_fb_post_page_message_chat_bot(page_token, sender_id, response)
        elif object == "instagram":
            ig_profile = InstagramProfile.objects.get(business_id = page_id)
            ig_id = ig_profile.id
            page_token = ig_profile.token
            connected_facebook_page_id = ig_profile.connected_facebook_page_id
            
            campaign_id_list = []
            try:
                campaign_datas = db.api_campaign.find({'instagram_profile_id': ig_id, 'start_at': {'$lt': datetime.utcnow()}, 'end_at': {'$gt': datetime.utcnow()}})
                for campaign_data in campaign_datas:
                    campaign_id_list.append(campaign_data['id'])
            except Exception:
                campaign_id_list.append(-1)
                
            comment_count = db.api_campaign_comment.find({'campaign_id':{'$in': campaign_id_list}, 'customer_id': sender_id, 'platform': 'instagram'}).count()
            if comment_count > 0:
                output_msg_list = get_ig_auto_response(ig_id, message['text'])
                print("output_msg_list", output_msg_list)
                for output_msg in output_msg_list:

                    service.instagram.chat_bot.post_page_message_chat_bot(connected_facebook_page_id, page_token, sender_id, output_msg)
            else:
                print ('user not commented before')
                
            # output_msg_list = get_ig_auto_response(ig_id, message['text'])
            # print("output_msg_list", output_msg_list)
            # for output_msg in output_msg_list:
            #     response = {'text': output_msg}
            #     service.instagram.chat_bot.post_page_message_chat_bot(connected_facebook_page_id, page_token, sender_id, response)

    except Exception as e:
        print(e)
        return -1
