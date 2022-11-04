from api import models
from datetime import datetime
import service
import database
import lib


def handle_auto_response(object, page_id, sender_id, message):
    # text = str(message.get('text','')).encode('latin1').decode('unicode_escape')#.encode('latin1').decode('utf8')
    text = message.get('text','')
    text = text.replace('\n',' ')
    text:str = lib.util.text_processor.remove_punctuation(text)

    words = text.split(' ')
    bi_grams = lib.util.text_processor.get_bi_grams(text)
    tri_grams = lib.util.text_processor.get_tri_grams(text)

    keywords = words + bi_grams + tri_grams


    if object == "page":

        facebook_page = models.facebook.facebook_page.FacebookPage.objects.get(page_id = page_id)
        
        auto_responses_data = database.lss.auto_response.AutoResponse.filter(facebook_page_id=facebook_page.id,input_msg={'$in':keywords})

        for auto_response_data in auto_responses_data:
            service.facebook.chat_bot.post_page_text_message_chat_bot(facebook_page.token, sender_id, auto_response_data.get('output_msg'))


    elif object == "instagram":
        ig_profile = models.instagram.instagram_profile.InstagramProfile.objects.get(business_id = page_id)
        ig_id = ig_profile.id
        page_token = ig_profile.token
        connected_facebook_page_id = ig_profile.connected_facebook_page_id

        auto_responses_data = database.lss.auto_response.AutoResponse.filter(instagram_profile_id=ig_id,input_msg={'$in':keywords})

        for auto_response_data in auto_responses_data:
            service.instagram.chat_bot.post_page＿text_message_chat_bot(connected_facebook_page_id, page_token, sender_id, auto_response_data.get('output_msg'))


