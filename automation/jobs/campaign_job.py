import os
import config
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception:
    pass
from django.conf import settings

from backend.pymongo.mongodb import db

from automation import jobs
import lib
import service
import requests
import traceback
from dateutil import parser

class OrderCodesMappingSingleton:

    order_codes_mapping = None

    @classmethod
    def get_mapping(cls, campaign_id):
        if cls.order_codes_mapping == None:
            campaign_products = db.api_campaign_product.find(
                {"campaign_id": campaign_id, "$or": [{"type": "product"}, {"type": "product-fast"}]})
            cls.order_codes_mapping = {campaign_product['order_code'].lower(): campaign_product
                                for campaign_product in campaign_products}
        return cls.order_codes_mapping


@lib.error_handle.error_handler.campaign_job_error_handler.campaign_job_error_handler
# @campaign_job_error_handler
def campaign_job(campaign_id):

    logs=[]
    campaign = db.api_campaign.find_one({"id": campaign_id})
    capture_facebook(campaign, logs)
    capture_youtube(campaign, logs)
    capture_instagram(campaign, logs)
    lib.util.logger.print_table(["Campaign ID", campaign_id],logs)

# @capture_platform_error_handler
@lib.error_handle.error_handler.capture_platform_error_handler.capture_platform_error_handler
def capture_facebook(campaign, logs):
    logs.append(["facebook",""])
    if not campaign['facebook_page_id']:
        return

    facebook_page = db.api_facebook_page.find_one(
        {"id": campaign['facebook_page_id']})

    if not facebook_page:
        logs.append(["error","no facebook_page found"])
        return

    page_token = facebook_page.get('token')
    facebook_campaign = campaign.get('facebook_campaign',{})
    post_id = facebook_campaign.get('post_id', '')
    since = facebook_campaign.get('comment_capture_since', 1)

    if not page_token or not post_id:
        return

    
    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign['id'])
    
    code, data = service.facebook.post.get_post_comments(page_token, post_id, since)
    logs.append(["post_id",post_id])
    logs.append(["since",since])
    logs.append(["code",code])

    if code // 100 != 2 :
        facebook_campaign['post_id'] = ''
        facebook_campaign['remark'] = f'Facebook API error: {data["error"]}'
        db.api_campaign.update_one({'id': campaign.get('id')}, {
                                   '$set': {"facebook_campaign": facebook_campaign}})
        return

    comment_capture_since = since
    comments = data.get('data', [])

    if comments and int(comments[-1].get('created_time')) == since:
        logs.append(["number of comments",0])
        return

    logs.append(["number of comments", len(comments)])
    try:
        for comment in comments:
            logs.append(["message", comment.get('message')])

            if not comment.get('from',{}).get('id'):
                logs.append(["error", "can't get user"])
                continue

            if comment.get('from',{}).get('id') == facebook_page.get('page_id'):
                comment_capture_since = comment.get('created_time')
                continue

            uni_format_comment = {
                'platform': 'facebook',
                'id': comment['id'],
                "campaign_id": campaign['id'],
                'message': comment['message'],
                "created_time": comment['created_time'],
                "customer_id": comment['from']['id'],
                "customer_name": comment['from']['name'],
                "image": comment['from']['picture']['data']['url'],
                "categories":service.nlp.classification.classify_comment_v1(texts=[[comment['message']]],threshold=0.9)
                }
            db.api_campaign_comment.insert_one(uni_format_comment)
            service.rq.job.enqueue_comment_queue(jobs.comment_job.comment_job,campaign, 'facebook', facebook_page, uni_format_comment, order_codes_mapping)
            comment_capture_since = comment['created_time']
    except Exception as e:
        print(traceback.format_exc())
        

    facebook_campaign['comment_capture_since'] = comment_capture_since
    db.api_campaign.update_one({'id': campaign['id']}, {
                               "$set": {'facebook_campaign': facebook_campaign}})

@lib.error_handle.error_handler.capture_platform_error_handler.capture_platform_error_handler
def capture_youtube(campaign, logs):
    logs.append(["youtube",""])
    # if not campaign['youtube_channel_id']:
    #     return

    youtube_channel = db.api_youtube_channel.find_one(
                {'id': campaign['youtube_channel_id']})
    if not youtube_channel:
        logs.append(["error", "no youtube_channel found"])
        return
        
    access_token = youtube_channel.get('token')
    refresh_token = youtube_channel.get('refresh_token')

    if not access_token or not refresh_token:
        logs.append(["error", "need both access_token and refresh_token"])
        return

    youtube_campaign = campaign['youtube_campaign']

    next_page_token = youtube_campaign.get('next_page_token', '')
    
    

    
    if youtube_campaign.get('live_chat_ended',False):
        capture_youtube_video(campaign, youtube_channel, logs)
        return

    live_chat_id = youtube_campaign.get('live_chat_id')
    if not live_chat_id:
        live_video_id = youtube_campaign.get('live_video_id')
        if not live_video_id:
            logs.append(["error", "no live_video_id"])
            return
        
        code, data = service.youtube.viedo.get_video_info_with_access_token(access_token, live_video_id)
        if code // 100 != 2:
            if code == 401:
                refresh_youtube_channel_token(youtube_channel)
            logs.append(["error", "video info error"])
            print(data)
            return
        items = data.get("items")
        if not items:
            logs.append(["error", "no items"])
            return

        liveStreamingDetails = items[0].get('liveStreamingDetails')

        if not liveStreamingDetails:
            logs.append(["error", "no liveStreamingDetails"])
            return

        if 'actualEndTime' in liveStreamingDetails.keys():
            youtube_campaign['live_chat_ended'] = True
            db.api_campaign.update_one({'id': campaign['id']}, {
                                    '$set': {"youtube_campaign":youtube_campaign}})
            return
            
        live_chat_id = liveStreamingDetails.get('activeLiveChatId')
        if not live_chat_id:
            logs.append(["error", "can't get live_chat_id"])
            return

        #start of every youtube live chat:
        youtube_campaign['live_chat_id'] = live_chat_id
        db.api_campaign.update_one({'id': campaign['id']}, { "$set": {'youtube_campaign': youtube_campaign}})
        access_token = refresh_youtube_channel_token(youtube_channel)

    
    code, data = service.youtube.live_chat.get_live_chat_comment_with_access_token(access_token, next_page_token, live_chat_id, 100)

    logs.append(["live_chat_id", live_chat_id])
    logs.append(["next_page_token", next_page_token])
    logs.append(["code", code])

    if code // 100 != 2 and 'error' in data:
        if code == 401:
            access_token = refresh_youtube_channel_token(youtube_channel)
            return

        youtube_campaign['live_chat_id'] = ''
        youtube_campaign['next_page_token'] = ''
        youtube_campaign['remark'] = 'youtube API error'
        db.api_campaign.update_one({'id': campaign['id']}, {
                                   '$set': {"youtube_campaign":youtube_campaign}})
        return

    next_page_token = data['nextPageToken']
    comments = data.get('items', [])
    logs.append(["number of comments", len(comments)])

    if not comments:
        return

    is_failed = youtube_campaign.get('is_failed')
    latest_comment_time = youtube_campaign.get('latest_comment_time', 1)

    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign['id'])

    try:
        for comment in comments:
            logs.append(["message", comment['snippet']['displayMessage']])

            comment_time_stamp = parser.parse(
                comment['snippet']['publishedAt']).timestamp()

            if comment['authorDetails']['channelId'] == youtube_channel.get('channel_id'):
                continue

            if is_failed and comment_time_stamp > latest_comment_time:
                continue

            uni_format_comment = {
                'platform': 'youtube',
                'id': comment['id'],
                "campaign_id": campaign['id'],
                'message': comment['snippet']['displayMessage'],
                "created_time": comment_time_stamp,
                "customer_id": comment['authorDetails']['channelId'],
                "customer_name": comment['authorDetails']['displayName'],
                "image": comment['authorDetails']['profileImageUrl'],
                "live_chat_id": live_chat_id,
                "categories":service.nlp.classification.classify_comment_v1(texts=[[comment['snippet']['displayMessage']]],threshold=0.9)
            }
            db.api_campaign_comment.insert_one(uni_format_comment)

            service.rq.job.enqueue_comment_queue(jobs.comment_job.comment_job, campaign, 'youtube', youtube_channel, uni_format_comment, order_codes_mapping)
        youtube_campaign['next_page_token'] = data.get('nextPageToken', "")
        youtube_campaign['latest_comment_time'] = parser.parse(
            comments[-1]['snippet']['publishedAt']).timestamp()
        youtube_campaign['is_failed'] = False

        # if youtube_campaign.get('last_refresh_timestamp',1)+3000 <= datetime.timestamp(datetime.now()):
        #     youtube_campaign = get_youtube_refresh_token(youtube_campaign, refresh_token)

        db.api_campaign.update_one({'id': campaign['id']}, {
                                   "$set": {'youtube_campaign': youtube_campaign}})
    except Exception as e:
        print(traceback.format_exc())
        latest_campaign_comment = db.api_campaign_comment.find_one(
            {'platform': 'youtube', 'campaign_id': campaign['id']}, sort=[('created_time', -1)])
        youtube_campaign['is_failed'] = True
        youtube_campaign['latest_comment_time'] = latest_campaign_comment['created_time'] if latest_campaign_comment else 1
        db.api_campaign.update_one({'id': campaign['id']}, {
                                   "$set": {'youtube_campaign': youtube_campaign}})
        return

# @capture_platform_error_handler
@lib.error_handle.error_handler.capture_platform_error_handler.capture_platform_error_handler
def capture_instagram(campaign, logs):
    logs.append(["instagram",""])
    
    if not campaign['instagram_profile_id']:
        return

    instagram_profile = db.api_instagram_profile.find_one(
        {'id': int(campaign['instagram_profile_id'])})

    if not instagram_profile:
        logs.append(["error", "no instagram_profile found"])
        return

    page_token = instagram_profile['token']
    instagram_campaign = campaign['instagram_campaign']
    live_media_id = instagram_campaign.get('live_media_id')

    if not page_token or not live_media_id:
        logs.append(["error", "no page_token or live_media_id"])
        return

    last_crelast_create_message_id = instagram_campaign.get("last_create_message_id")
    
    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign['id'])
    
    after_page = None

    keep_capturing = True

    while keep_capturing :
        code, get_ig_comments_response = service.instagram.post.get_post_comments(page_token, live_media_id, after_page)

        logs.append(["live_media_id", live_media_id])
        logs.append(["code", code])

        if code // 100 != 2 and 'error' in get_ig_comments_response and get_ig_comments_response['error']['type'] in ('GraphMethodException', 'OAuthException'):
            # instagram_campaign['live_media_id'] = ''
            instagram_campaign['remark'] = f'Instagram API error: {get_ig_comments_response["error"]}'
            db.api_campaign.update_one({'id': campaign['id']}, {
                                    '$set': {"instagram_campaign": instagram_campaign}})
            return

        comments = get_ig_comments_response.get('data', [])

        if not comments:
            return 

        if not after_page:
            new_last_crelast_create_message_id = comments[0]['id']

        logs.append(["number of comments", len(comments)])

        for comment in comments:

            if comment['id'] == last_crelast_create_message_id:
                keep_capturing = False
                break

            from_info = service.instagram.user.get_id_from(page_token, comment['id'])
            profile_img_url = service.instagram.user.get_profile_picture(
                page_token, from_info[1]['from']['id'])
            img_url = ''

            if profile_img_url[0] == 400:
                img_url == ''
            if profile_img_url[0] == 200:
                img_url = profile_img_url[1]['profile_picture_url']

            uni_format_comment = {
                'platform': 'instagram',
                'id': comment['id'],
                "campaign_id": campaign['id'],
                'message': comment['text'],
                "created_time": comment['timestamp'],  #parse to timestamp
                "customer_id": from_info[1]['from']['username'],   #
                "customer_name": from_info[1]['from']['username'],  #
                "image": img_url,
                "categories":service.nlp.classification.classify_comment_v1(texts=[[comment['text']]],threshold=0.9)
                }   #
            db.api_campaign_comment.insert_one(uni_format_comment)
            service.rq.job.enqueue_comment_queue(jobs.comment_job.comment_job, campaign, 'instagram', instagram_profile, uni_format_comment, order_codes_mapping)
            

        if keep_capturing:
            after_page = get_ig_comments_response.get('paging', {}).get('cursors', {}).get('after', None)

        if not after_page:
            keep_capturing = False

    instagram_campaign['is_failed'] = False
    instagram_campaign['last_create_message_id'] = new_last_crelast_create_message_id
    db.api_campaign.update_one({'id': campaign['id']}, {
        "$set": {'instagram_campaign': instagram_campaign}})

    


def capture_youtube_video(campaign, youtube_channel, logs):
    youtube_campaign = campaign['youtube_campaign']
    # refresh_token = youtube_campaign.get('refresh_token')
    next_page_token = youtube_campaign.get('next_page_token', '')
    live_video_id = youtube_campaign.get('live_video_id')
    
    # is_live_end = True

    keep_capturing = True

    # is_failed = youtube_campaign.get('is_failed', False)
    last_create_message_id = youtube_campaign.get("last_create_message_id")
    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign['id'])
    
    while keep_capturing :
        code, get_yt_video_data = service.youtube.viedo.get_video_comment_thread(next_page_token, live_video_id, 10)
        
        logs.append(["video_id", live_video_id])
        logs.append(["code", code])

        if code // 100 != 2 and 'error' in get_yt_video_data:


            #TODO handle token expired:

            # youtube_campaign['live_video_id'] = ''
            youtube_campaign['live_chat_id'] = ''
            youtube_campaign['next_page_token'] = ''
            youtube_campaign['remark'] = 'youtube API error'
            db.api_campaign.update_one({'id': campaign['id']}, {
                                    '$set': {"youtube_campaign":youtube_campaign}})
            return
        
        items = get_yt_video_data.get('items', [])
        if not items:
            return
        
        if not next_page_token:
            last_create_message_id = items[0]['snippet']['topLevelComment']['id']

        logs.append(["number of comments", len(items)])
        
        for comment in items:
            if comment['id'] == last_create_message_id:
                keep_capturing = False
                logs.append(["status", "no new comment !!"])
                break
            
            logs.append(["message", comment['snippet']['topLevelComment']['snippet']['textDisplay']])

            comment_time_stamp = parser.parse(
                comment['snippet']['topLevelComment']['snippet']['publishedAt']).timestamp()
            
            uni_format_comment = {
                'platform': 'youtube',
                'id': comment['snippet']['topLevelComment']['id'],
                "campaign_id": campaign['id'],
                'message': comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                "created_time": comment_time_stamp,
                "customer_id": comment['snippet']['topLevelComment']['snippet']['authorChannelId']['value'],
                "customer_name": comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                "image": comment['snippet']['topLevelComment']['snippet']['authorProfileImageUrl'],
                "categories":service.nlp.classification.classify_comment_v1(texts=[[comment['snippet']['topLevelComment']['snippet']['textDisplay']]],threshold=0.9)
            }
            db.api_campaign_comment.insert_one(uni_format_comment)
            service.rq.job.enqueue_comment_queue(jobs.comment_job.comment_job, 
                campaign, 'youtube', youtube_channel, uni_format_comment, order_codes_mapping)
        if keep_capturing:
            next_page_token = get_yt_video_data.get('nextPageToken', '')

        if not next_page_token:
            keep_capturing = False
        
    youtube_campaign['is_failed'] = False
    youtube_campaign['last_create_message_id'] = last_create_message_id
    youtube_campaign['next_page_token'] = next_page_token

    db.api_campaign.update_one({'id': campaign['id']}, {
        "$set": {'youtube_campaign': youtube_campaign}})




def refresh_youtube_channel_token(youtube_channel, logs):
    logs.append(["event", "refreshing token..."])
    response = requests.post(
    url="https://accounts.google.com/o/oauth2/token",
    data={
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,  #TODO keep it to settings
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,                                 #TODO keep it to settings
        "grant_type": "refresh_token",
        "refresh_token": youtube_channel.get("refresh_token")
    },)

    code, refresh_token_response = response.status_code, response.json()
    # code, refresh_token_response = api_google_post_refresh_token(refresh_token)

    logs.append(["refresh status", code])
    logs.append(["refresh data", refresh_token_response])

    db.api_youtube_channel.update_one({"id":youtube_channel.get('id')},{"$set":{"token":refresh_token_response.get('access_token')}})
    return refresh_token_response.get('access_token')