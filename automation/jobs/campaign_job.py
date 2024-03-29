import os
import config
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception:
    pass
from django.conf import settings

from automation import jobs
import service
import requests
import traceback
from dateutil import parser
from datetime import datetime
import database
from api import models
from lib.error_handle.error_handler import campaign_job_error_handler, capture_platform_error_handler
from lib import util
import numpy
C_VALUE = 60
LOWEST_PRIORITY = 3
class OrderCodesMappingSingleton:

    order_codes_mapping = None

    @classmethod
    def get_mapping(cls, campaign_id):
        if cls.order_codes_mapping == None:
            kwargs = {"campaign_id": campaign_id, "$or": [{"type": "product"}, {"type": "product-fast"}]}
            campaign_products = database.lss.campaign_product.CampaignProduct.filter(**kwargs)

            lenlist=[]
            campaign_product_list=[]
            for campaign_product in campaign_products:

                if not campaign_product.get('order_code'):
                    continue
                lenlist.append(len(campaign_product.get('order_code')))
                campaign_product_list.append(campaign_product)
            sorted_index = numpy.argsort(lenlist)[::-1]
            cls.order_codes_mapping = {campaign_product_list[index]['order_code'].lower(): campaign_product_list[index]
                                for index in sorted_index}

            # cls.order_codes_mapping = {campaign_product['order_code'].lower(): campaign_product
            #                     for campaign_product in campaign_products}
        return cls.order_codes_mapping

@campaign_job_error_handler.campaign_job_error_handler
def campaign_job(campaign_id):

    logs=[]
    campaign = database.lss.campaign.Campaign.get_object(id=campaign_id)
    user_subscription_data = database.lss.user_subscription.UserSubscription.get(id=campaign.data.get('user_subscription_id'))

    capture_facebook_v2(campaign, user_subscription_data, logs)
    capture_sub_facebook_v2(campaign, user_subscription_data, logs, index=0)
    capture_sub_facebook_v2(campaign, user_subscription_data, logs, index=3)
    capture_sub_facebook_v2(campaign, user_subscription_data, logs, index=4)
    capture_sub_facebook_v2(campaign, user_subscription_data, logs, index=5)
    capture_sub_facebook_v2(campaign, user_subscription_data, logs, index=6)
    capture_youtube_v2(campaign, user_subscription_data, logs)
    capture_instagram_v2(campaign, user_subscription_data, logs)
    util.logger.print_table(["Campaign ID", campaign_id],logs)


@capture_platform_error_handler.capture_platform_error_handler
def capture_facebook(campaign, user_subscription_data, logs):
    logs.append(["facebook",""])
    if not campaign.data.get('facebook_page_id'):
        return
    facebook_page = database.lss.facebook_page.FacebookPage.get_object(id=campaign.data.get('facebook_page_id'))

    if not facebook_page:
        logs.append(["error","no facebook_page found"])
        return

    page_token = facebook_page.data.get('token')
    facebook_campaign = campaign.data.get('facebook_campaign',{})
    post_id = facebook_campaign.get('post_id', '')
    since = facebook_campaign.get('comment_capture_since', 1)

    if not page_token or not post_id:
        return

    
    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign.id)
    
    code, data = service.facebook.post.get_post_comments(page_token, post_id, since)
    logs.append(["post_id",post_id])
    logs.append(["since",since])
    logs.append(["code",code])

    if code // 100 != 2 :
        print(data)
        facebook_campaign['post_id'] = ''
        facebook_campaign['remark'] = f'Facebook API error: {data["error"]}'
        campaign.update(facebook_campaign=facebook_campaign, sync=False)
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

            if comment.get('from',{}).get('id') == facebook_page.data.get('page_id'):
                comment_capture_since = comment.get('created_time')
                continue

            uni_format_comment = {
                'platform': 'facebook',
                'id': comment['id'],
                "campaign_id": campaign.id,
                'message': comment['message'],
                "created_time": comment['created_time'],
                "customer_id": comment['from']['id'],
                "customer_name": comment['from']['name'],
                "image": comment['from']['picture']['data']['url'],
                "categories":service.nlp.classification.classify_comment_v2(texts=[comment['message']])
                }
            try:
                database.lss.campaign_comment.CampaignComment.create(**uni_format_comment, auto_inc=False)
            except Exception: #duplicate key error might happen here
                continue
            service.channels.campaign.send_comment_data(campaign.id, uni_format_comment)
            service.rq.queue.enqueue_comment_queue(jobs.comment_job_v2.comment_job, campaign.data, user_subscription_data, 'facebook', facebook_page.data, uni_format_comment, order_codes_mapping)
            comment_capture_since = comment['created_time']
    except Exception as e:
        print(traceback.format_exc())
        

    facebook_campaign['comment_capture_since'] = comment_capture_since
    campaign.update(facebook_campaign=facebook_campaign, sync=False)

@capture_platform_error_handler.capture_platform_error_handler
def capture_youtube(campaign, user_subscription_data, logs):
    logs.append(["youtube",""])

    if not campaign.data.get('youtube_channel_id'):
        return

    youtube_channel = database.lss.youtube_channel.YoutubeChannel.get_object(id=campaign.data.get('youtube_channel_id'))
    if not youtube_channel:
        logs.append(["error", "no youtube_channel found"])
        return
        
    access_token = youtube_channel.data.get('token')
    refresh_token = youtube_channel.data.get('refresh_token')

    if not access_token or not refresh_token:
        logs.append(["error", "need both access_token and refresh_token"])
        return

    youtube_campaign = campaign.data.get('youtube_campaign')

    next_page_token = youtube_campaign.get('next_page_token', '')
    
    

    
    if youtube_campaign.get('live_chat_ended',False):
        capture_youtube_video(campaign, user_subscription_data, youtube_channel, logs)
        return

    live_chat_id = youtube_campaign.get('live_chat_id')
    if not live_chat_id:
        live_video_id = youtube_campaign.get('live_video_id')
        if not live_video_id:
            logs.append(["error", "no live_video_id"])
            return
        
        code, data = service.youtube.viedo.get_video_info_with_access_token(access_token, live_video_id)
        if code // 100 != 2:
            print(data)
            if code == 401:
                refresh_youtube_channel_token(youtube_channel, logs)
            logs.append(["error", "video info error"])
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
            campaign.update(youtube_campaign=youtube_campaign, sync=False)
            return
            
        live_chat_id = liveStreamingDetails.get('activeLiveChatId')
        if not live_chat_id:
            logs.append(["error", "can't get live_chat_id"])
            return

        #start of every youtube live chat:
        youtube_campaign['live_chat_id'] = live_chat_id
        campaign.update(youtube_campaign=youtube_campaign, sync=False)
        access_token = refresh_youtube_channel_token(youtube_channel, logs)

    
    code, data = service.youtube.live_chat.get_live_chat_comment_with_access_token(access_token, next_page_token, live_chat_id, 100)

    logs.append(["live_chat_id", live_chat_id])
    logs.append(["next_page_token", next_page_token])
    logs.append(["code", code])

    if code // 100 != 2 and 'error' in data:
        print(data)
        if code == 401:
            access_token = refresh_youtube_channel_token(youtube_channel, logs)
            return

        youtube_campaign['live_chat_id'] = ''
        youtube_campaign['next_page_token'] = ''
        youtube_campaign['remark'] = 'youtube API error'
        campaign.update(youtube_campaign=youtube_campaign, sync=False)
        return

    next_page_token = data['nextPageToken']
    comments = data.get('items', [])
    logs.append(["number of comments", len(comments)])

    if not comments:
        return

    is_failed = youtube_campaign.get('is_failed')
    latest_comment_time = youtube_campaign.get('latest_comment_time', 1)

    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign.id)

    try:
        for comment in comments:
            logs.append(["message", comment['snippet']['displayMessage']])

            comment_time_stamp = parser.parse(
                comment['snippet']['publishedAt']).timestamp()

            if comment['authorDetails']['channelId'] == youtube_channel.data.get('channel_id'):
                continue

            if is_failed and comment_time_stamp > latest_comment_time:
                continue

            uni_format_comment = {
                'platform': 'youtube',
                'id': comment['id'],
                "campaign_id": campaign.id,
                'message': comment['snippet']['displayMessage'],
                "created_time": comment_time_stamp,
                "customer_id": comment['authorDetails']['channelId'],
                "customer_name": comment['authorDetails']['displayName'],
                "image": comment['authorDetails']['profileImageUrl'],
                "live_chat_id": live_chat_id,
                "categories":service.nlp.classification.classify_comment_v2(texts=[comment['snippet']['displayMessage']])
            }
            try:
                database.lss.campaign_comment.CampaignComment.create(**uni_format_comment, auto_inc=False)
            except Exception:
                continue
            service.channels.campaign.send_comment_data(campaign.id, uni_format_comment)
            service.rq.queue.enqueue_comment_queue(jobs.comment_job_v2.comment_job, campaign.data, user_subscription_data, 'youtube', youtube_channel.data, uni_format_comment, order_codes_mapping)

            # service.rq.queue.enqueue_comment_queue(jobs.comment_job.comment_job, campaign.data, user_subscription_data, 'youtube', youtube_channel.data, uni_format_comment, order_codes_mapping)
        youtube_campaign['next_page_token'] = data.get('nextPageToken', "")
        youtube_campaign['latest_comment_time'] = parser.parse(
            comments[-1]['snippet']['publishedAt']).timestamp()
        youtube_campaign['is_failed'] = False

        # if youtube_campaign.get('last_refresh_timestamp',1)+3000 <= datetime.timestamp(datetime.now()):
        #     youtube_campaign = get_youtube_refresh_token(youtube_campaign, refresh_token)
        campaign.update(youtube_campaign=youtube_campaign, sync=False)

    except Exception as e:
        print(traceback.format_exc())
        latest_campaign_comment = database.lss.campaign_comment.CampaignComment.get_latest_comment_object(campaign.id, 'youtube')
        youtube_campaign['is_failed'] = True
        youtube_campaign['latest_comment_time'] = latest_campaign_comment.data.get('created_time') if latest_campaign_comment else 1
        campaign.update(youtube_campaign=youtube_campaign, sync=False)
        return


@capture_platform_error_handler.capture_platform_error_handler
def capture_instagram(campaign, user_subscription_data, logs):
    logs.append(["instagram",""])
    
    if not campaign.data.get('instagram_profile_id'):
        return
    instagram_profile = database.lss.instagram_profile.InstagramProfile.get_object(id=campaign.data.get('instagram_profile_id'))


    if not instagram_profile:
        logs.append(["error", "no instagram_profile found"])
        return

    page_token = instagram_profile.data.get('token')
    instagram_campaign = campaign.data.get('instagram_campaign')
    live_media_id = instagram_campaign.get('live_media_id')

    if not live_media_id:
        logs.append(["error", "no live_media_id"])
        return

    if not page_token :
        logs.append(["error", "no page_token"])
        return


    last_crelast_create_message_id = instagram_campaign.get("last_create_message_id")
    
    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign.id)
    
    after_page = None

    keep_capturing = True

    while keep_capturing :
        code, get_ig_comments_response = service.instagram.post.get_post_comments(page_token, live_media_id, after_page)

        logs.append(["live_media_id", live_media_id])
        logs.append(["code", code])

        if code // 100 != 2 and 'error' in get_ig_comments_response and get_ig_comments_response['error']['type'] in ('GraphMethodException', 'OAuthException'):
            # instagram_campaign['live_media_id'] = ''
            print(get_ig_comments_response)
            instagram_campaign['remark'] = f'Instagram API error: {get_ig_comments_response["error"]}'
            campaign.update(instagram_campaign=instagram_campaign, sync=False)
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

            # from_info = service.instagram.user.get_id_from(page_token, comment['id'])
            profile_img_url = service.instagram.user.get_profile_picture(
                page_token, comment['from']['id'])
            img_url = ''

            if profile_img_url[0] == 400:
                img_url == ''
            if profile_img_url[0] == 200:
                img_url = profile_img_url[1]['profile_pic']

            uni_format_comment = {
                'platform': 'instagram',
                'id': comment['id'],
                "campaign_id": campaign.id,
                'message': comment['text'],
                "created_time": datetime.timestamp(parser.parse(comment['timestamp'])),  
                "customer_id": comment['from']['id'],   
                "customer_name": comment['from']['username'],  
                "image": img_url,
                "categories":service.nlp.classification.classify_comment_v2(texts=[comment['text']])
                }   #
            try:
                database.lss.campaign_comment.CampaignComment.create(**uni_format_comment, auto_inc=False)
            except Exception:
                continue
            service.channels.campaign.send_comment_data(campaign.id, uni_format_comment)
            service.rq.queue.enqueue_comment_queue(jobs.comment_job_v2.comment_job, campaign.data, user_subscription_data, 'instagram', instagram_profile.data, uni_format_comment, order_codes_mapping)
            

        if keep_capturing:
            after_page = get_ig_comments_response.get('paging', {}).get('cursors', {}).get('after', None)

        if not after_page:
            keep_capturing = False

    instagram_campaign['is_failed'] = False
    instagram_campaign['last_create_message_id'] = new_last_crelast_create_message_id
    campaign.update(instagram_campaign=instagram_campaign, sync=False)
    


def capture_youtube_video(campaign, user_subscription_data, youtube_channel, logs):
    youtube_campaign = campaign.data.get('youtube_campaign')
    # refresh_token = youtube_campaign.get('refresh_token')
    next_page_token = youtube_campaign.get('next_page_token', '')
    live_video_id = youtube_campaign.get('live_video_id')
    
    # is_live_end = True

    keep_capturing = True

    # is_failed = youtube_campaign.get('is_failed', False)
    last_create_message_id = youtube_campaign.get("last_create_message_id")
    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign.id)
    
    while keep_capturing :
        code, get_yt_video_data = service.youtube.viedo.get_video_comment_thread(next_page_token, live_video_id, 10)
        
        logs.append(["video_id", live_video_id])
        logs.append(["code", code])

        if code // 100 != 2 and 'error' in get_yt_video_data:
            print(get_yt_video_data)

            #TODO handle token expired:

            # youtube_campaign['live_video_id'] = ''
            youtube_campaign['live_chat_id'] = ''
            youtube_campaign['next_page_token'] = ''
            youtube_campaign['remark'] = 'youtube API error'
            campaign.update(youtube_campaign=youtube_campaign,sync=False)
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
                "campaign_id": campaign.id,
                'message': comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                "created_time": comment_time_stamp,
                "customer_id": comment['snippet']['topLevelComment']['snippet']['authorChannelId']['value'],
                "customer_name": comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                "image": comment['snippet']['topLevelComment']['snippet']['authorProfileImageUrl'],
                "categories":service.nlp.classification.classify_comment_v2(texts=[comment['snippet']['topLevelComment']['snippet']['textDisplay']])
            }

            try:
                database.lss.campaign_comment.CampaignComment.create(**uni_format_comment, auto_inc=False)
            except Exception:
                continue
            service.rq.queue.enqueue_comment_queue(jobs.comment_job.comment_job, 
                campaign.data, user_subscription_data, 'youtube', youtube_channel.data, uni_format_comment, order_codes_mapping)
        if keep_capturing:
            next_page_token = get_yt_video_data.get('nextPageToken', '')

        if not next_page_token:
            keep_capturing = False
        
    youtube_campaign['is_failed'] = False
    youtube_campaign['last_create_message_id'] = last_create_message_id
    youtube_campaign['next_page_token'] = next_page_token
    campaign.update(youtube_campaign=youtube_campaign,sync=False)



def refresh_youtube_channel_token(youtube_channel, logs):
    logs.append(["event", "refreshing token..."])
    response = requests.post(
    url="https://accounts.google.com/o/oauth2/token",
    data={
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,  #TODO keep it to settings
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,                                 #TODO keep it to settings
        "grant_type": "refresh_token",
        "refresh_token": youtube_channel.data.get("refresh_token")
    },)

    code, refresh_token_response = response.status_code, response.json()
    # code, refresh_token_response = api_google_post_refresh_token(refresh_token)

    logs.append(["refresh status", code])
    logs.append(["refresh data", refresh_token_response])
    youtube_channel.update(token=refresh_token_response.get('access_token'),sync=False)

    return refresh_token_response.get('access_token')



@capture_platform_error_handler.capture_platform_error_handler
def capture_facebook_v2(campaign, user_subscription_data, logs, attempts=2):
    try:
        logs.append(["facebook",""])
        if not campaign.data.get('facebook_page_id'):
            return
        facebook_page = database.lss.facebook_page.FacebookPage.get_object(id=campaign.data.get('facebook_page_id'))

        if not facebook_page:
            logs.append(["error","no facebook_page found"])
            return

        page_token = facebook_page.data.get('token')
        facebook_campaign = campaign.data.get('facebook_campaign',{})
        post_id = facebook_campaign.get('post_id', '')
        facebook_comment_capture_since = facebook_campaign.get('comment_capture_since', 1)

        if not page_token or not post_id:
            return
        
        order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign.id)
        
        code, data = service.facebook.post.get_post_comments(page_token, post_id, since = facebook_comment_capture_since)
        logs.append(["post_id",post_id])
        logs.append(["since",facebook_comment_capture_since])
        logs.append(["code",code])

        if code // 100 != 2 :
            print(data)
            facebook_campaign['post_id'] = ''
            facebook_campaign['remark'] = f'Facebook API error: {data["error"]}'
            campaign.update(facebook_campaign=facebook_campaign, sync=False)
            return

        facebook_comments = data.get('data', [])

        if facebook_comments and int(facebook_comments[-1].get('created_time')) == facebook_comment_capture_since:
            logs.append(["number of comments",0])
            __update_campaign_silent_count(campaign)
            return

        if not facebook_comments:
            logs.append(["number of comments",0])
            __update_campaign_silent_count(campaign)
            return
            
        facebook_campaign['comment_capture_since'] = int(facebook_comments[-1].get('created_time'))
        campaign.update(
            facebook_campaign=facebook_campaign,
            priority=1,
            silent_count=0,
            sync=True)

        logs.append(["number of comments", len(facebook_comments)])

        try:
            for comment in facebook_comments:
                logs.append(["message", comment.get('message')])

                if not comment.get('from',{}).get('id'):
                    logs.append(["error", "can't get user"])
                    continue

                if comment.get('from',{}).get('id') == facebook_page.data.get('page_id'):
                    continue

                uni_format_comment = {
                    'platform': models.user.user_subscription.PLATFORM_FACEBOOK,
                    'id': comment['id'],
                    "campaign_id": campaign.id,
                    'message': comment['message'],
                    "created_time": comment['created_time'],
                    "customer_id": comment['from']['id'],
                    "customer_name": comment['from']['name'],
                    "image": comment['from']['picture']['data']['url'],
                    "categories":service.nlp.classification.classify_comment_v2(texts=[comment['message']]),
                }
                try:
                    database.lss.campaign_comment.CampaignComment.create(**uni_format_comment, auto_inc=False)
                except Exception:
                    continue

                service.channels.campaign.send_comment_data(campaign.id, uni_format_comment)
                service.rq.queue.enqueue_comment_queue(jobs.comment_job_v2.comment_job, campaign.data, user_subscription_data, models.user.user_subscription.PLATFORM_FACEBOOK, facebook_page.data, uni_format_comment, order_codes_mapping)

        except Exception:
            print(traceback.format_exc())
    
    except Exception:
        if attempts>0:
            print('retry')
            capture_facebook_v2(campaign, user_subscription_data, logs, attempts=attempts-1)
        print(traceback.format_exc())


@capture_platform_error_handler.capture_platform_error_handler
def capture_sub_facebook_v2(campaign, user_subscription_data, logs, index=0, attempts=2):
    try:
        postfix = f'_{index}' if index else ''
        logs.append(["facebook",""])
        if not campaign.data.get(f'sub_facebook_page{postfix}_id'):
            return
        facebook_page = database.lss.facebook_page.FacebookPage.get_object(id=campaign.data.get(f'sub_facebook_page{postfix}_id'))

        if not facebook_page:
            logs.append(["error","no sub facebook_page found"])
            return

        page_token = facebook_page.data.get('token')
        facebook_campaign = campaign.data.get(f'sub_facebook_campaign{postfix}',{})
        post_id = facebook_campaign.get('post_id', '')
        facebook_comment_capture_since = facebook_campaign.get('comment_capture_since', 1)

        if not page_token or not post_id:
            return
        
        order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign.id)
        
        code, data = service.facebook.post.get_post_comments(page_token, post_id, since = facebook_comment_capture_since)
        logs.append(["post_id",post_id])
        logs.append(["since",facebook_comment_capture_since])
        logs.append(["code",code])

        if code // 100 != 2 :
            print(data)
            facebook_campaign['post_id'] = ''
            facebook_campaign['remark'] = f'Facebook API error: {data["error"]}'
            campaign.update(sync=False, **{f'sub_facebook_campaign{postfix}':facebook_campaign})
            return

        facebook_comments = data.get('data', [])

        if facebook_comments and int(facebook_comments[-1].get('created_time')) == facebook_comment_capture_since:
            logs.append(["number of comments",0])
            __update_campaign_silent_count(campaign)
            return

        if not facebook_comments:
            logs.append(["number of comments",0])
            __update_campaign_silent_count(campaign)
            return
            
        facebook_campaign['comment_capture_since'] = int(facebook_comments[-1].get('created_time'))
        campaign.update(
            # sub_facebook_campaign=facebook_campaign,
            priority=1,
            silent_count=0,
            sync=True,
             **{f'sub_facebook_campaign{postfix}':facebook_campaign}
            )

        logs.append(["number of comments", len(facebook_comments)])

        try:
            for comment in facebook_comments:
                logs.append(["message", comment.get('message')])

                if not comment.get('from',{}).get('id'):
                    logs.append(["error", "can't get user"])
                    continue

                if comment.get('from',{}).get('id') == facebook_page.data.get('page_id'):
                    continue

                uni_format_comment = {
                    'platform': models.user.user_subscription.PLATFORM_FACEBOOK,
                    'id': comment['id'],
                    "campaign_id": campaign.id,
                    'message': comment['message'],
                    "created_time": comment['created_time'],
                    "customer_id": comment['from']['id'],
                    "customer_name": comment['from']['name'],
                    "image": comment['from']['picture']['data']['url'],
                    "categories":service.nlp.classification.classify_comment_v2(texts=[comment['message']]),
                }
                try:
                    database.lss.campaign_comment.CampaignComment.create(**uni_format_comment, auto_inc=False)
                except Exception:
                    continue

                service.channels.campaign.send_comment_data(campaign.id, uni_format_comment)
                service.rq.queue.enqueue_comment_queue(jobs.comment_job_v2.comment_job, campaign.data, user_subscription_data, models.user.user_subscription.PLATFORM_FACEBOOK, facebook_page.data, uni_format_comment, order_codes_mapping)

        except Exception:
            print(traceback.format_exc())
    
    except Exception:
        if attempts>0:
            print('retry')
            capture_sub_facebook_v2(campaign, user_subscription_data, logs, index=index,attempts=attempts-1)
        print(traceback.format_exc())


@capture_platform_error_handler.capture_platform_error_handler
def capture_instagram_v2(campaign, user_subscription_data, logs, attempts=2):

    try:

        logs.append(["instagram",""])
        
        if not campaign.data.get('instagram_profile_id'):
            return
        instagram_profile = database.lss.instagram_profile.InstagramProfile.get_object(id=campaign.data.get('instagram_profile_id'))


        if not instagram_profile:
            logs.append(["error", "no instagram_profile found"])
            return

        page_token = instagram_profile.data.get('token')
        instagram_campaign = campaign.data.get('instagram_campaign')
        live_media_id = instagram_campaign.get('live_media_id')

        if not live_media_id:
            logs.append(["error", "no live_media_id"])
            return

        if not page_token :
            logs.append(["error", "no page_token"])
            return


        instagram_last_create_message_id = instagram_campaign.get("last_create_message_id")
        
        order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign.id)

        after_page =     None
        keep_capturing = True

        while keep_capturing :

            code, ig_comments_response = service.instagram.post.get_post_comments(page_token, live_media_id, after_page)

            logs.append(["live_media_id", live_media_id])
            logs.append(["code", code])

            if code // 100 != 2 and 'error' in ig_comments_response and ig_comments_response['error']['type'] in ('GraphMethodException', 'OAuthException'):
                print(ig_comments_response)
                instagram_campaign['remark'] = f'Instagram API error: {ig_comments_response["error"]}'
                campaign.update(instagram_campaign=instagram_campaign, sync=False)
                return

            instagram_comments = ig_comments_response.get('data', [])

            if not instagram_comments:
                __update_campaign_silent_count(campaign)
                return 
            
            if instagram_comments[0]['id'] == instagram_last_create_message_id:
                __update_campaign_silent_count(campaign)
                return 

            if not after_page:   #first run in the loop
                instagram_latest_message_id = instagram_comments[0]['id']
                instagram_campaign['last_create_message_id'] = instagram_latest_message_id
                campaign.update(
                    instagram_campaign=instagram_campaign,
                    priority=1,
                    silent_count=0,
                    sync=False)

            logs.append(["number of comments", len(instagram_comments)])

            for comment in instagram_comments:

                try:
                    if comment['id'] == instagram_last_create_message_id:
                        keep_capturing = False
                        break

                    profile_img_url = service.instagram.user.get_profile_picture(
                        page_token, comment['from']['id'])
                    img_url = ''

                    if profile_img_url[0] == 400:
                        img_url == ''
                    if profile_img_url[0] == 200:
                        img_url = profile_img_url[1]['profile_pic']

                    uni_format_comment = {
                        'platform': 'instagram',
                        'id': comment['id'],
                        "campaign_id": campaign.id,
                        'message': comment['text'],
                        "created_time": datetime.timestamp(parser.parse(comment['timestamp'])),  
                        "customer_id": comment['from']['id'],   
                        "customer_name": comment['from']['username'],  
                        "image": img_url,
                        "categories":service.nlp.classification.classify_comment_v2(texts=[comment['text']])
                        }   #
                    
                    
                    try:
                        database.lss.campaign_comment.CampaignComment.create(**uni_format_comment, auto_inc=False)
                    except Exception:
                        continue

                    service.channels.campaign.send_comment_data(campaign.id, uni_format_comment)
                    service.rq.queue.enqueue_comment_queue(jobs.comment_job_v2.comment_job, campaign.data, user_subscription_data, 'instagram', instagram_profile.data, uni_format_comment, order_codes_mapping)
                
                except Exception:
                    print(traceback.format_exc())
                    continue

            if keep_capturing:
                after_page = ig_comments_response.get('paging', {}).get('cursors', {}).get('after', None)

            if not after_page:
                keep_capturing = False

    except Exception:

        if attempts>0:
            capture_instagram_v2(campaign, user_subscription_data, logs, attempts=attempts-1)
        print(traceback.format_exc())



@capture_platform_error_handler.capture_platform_error_handler
def capture_youtube_v2(campaign, user_subscription_data, logs, attempts=2):
    logs.append(["youtube",""])

    if not campaign.data.get('youtube_channel_id'):
        return

    youtube_channel = database.lss.youtube_channel.YoutubeChannel.get_object(id=campaign.data.get('youtube_channel_id'))
    if not youtube_channel:
        logs.append(["error", "no youtube_channel found"])
        return
        
    access_token = youtube_channel.data.get('token')
    refresh_token = youtube_channel.data.get('refresh_token')

    if not access_token or not refresh_token:
        logs.append(["error", "need both access_token and refresh_token"])
        return

    youtube_campaign = campaign.data.get('youtube_campaign')

    next_page_token = youtube_campaign.get('next_page_token', '')
    
    

    
    if youtube_campaign.get('live_chat_ended',False):
        capture_youtube_video(campaign, user_subscription_data, youtube_channel, logs)
        return

    live_chat_id = youtube_campaign.get('live_chat_id')
    if not live_chat_id:
        live_video_id = youtube_campaign.get('live_video_id')
        if not live_video_id:
            logs.append(["error", "no live_video_id"])
            return
        
        code, data = service.youtube.viedo.get_video_info_with_access_token(access_token, live_video_id)
        if code // 100 != 2:
            print(data)
            if code == 401:
                refresh_youtube_channel_token(youtube_channel, logs)
            logs.append(["error", "video info error"])
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
            campaign.update(youtube_campaign=youtube_campaign, sync=False)
            return
            
        live_chat_id = liveStreamingDetails.get('activeLiveChatId')
        if not live_chat_id:
            logs.append(["error", "can't get live_chat_id"])
            return

        #start of every youtube live chat:
        youtube_campaign['live_chat_id'] = live_chat_id
        campaign.update(youtube_campaign=youtube_campaign, sync=False)
        access_token = refresh_youtube_channel_token(youtube_channel, logs)

    
    code, data = service.youtube.live_chat.get_live_chat_comment_with_access_token(access_token, next_page_token, live_chat_id, 100)

    logs.append(["live_chat_id", live_chat_id])
    logs.append(["next_page_token", next_page_token])
    logs.append(["code", code])

    if code // 100 != 2 and 'error' in data:
        print(data)
        if code == 401:
            access_token = refresh_youtube_channel_token(youtube_channel, logs)
            return

        youtube_campaign['live_chat_id'] = ''
        youtube_campaign['next_page_token'] = ''
        youtube_campaign['remark'] = 'youtube API error'
        campaign.update(youtube_campaign=youtube_campaign, sync=False)
        return

    next_page_token = data['nextPageToken']
    comments = data.get('items', [])
    logs.append(["number of comments", len(comments)])

    if not comments:
        __update_campaign_silent_count(campaign)
        return


    # latest_comment_time = youtube_campaign.get('latest_comment_time', 1)

    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign.id)


    youtube_campaign['next_page_token'] = data.get('nextPageToken', "")
    # youtube_campaign['latest_comment_time'] = parser.parse(
    #     comments[-1]['snippet']['publishedAt']).timestamp()
    
    campaign.update(
        youtube_campaign=youtube_campaign,
        priority=1,
        silent_count=0,
        sync=False)

    try:
        for comment in comments:
            logs.append(["message", comment['snippet']['displayMessage']])

            comment_time_stamp = parser.parse(
                comment['snippet']['publishedAt']).timestamp()

            if comment['authorDetails']['channelId'] == youtube_channel.data.get('channel_id'):
                continue

            uni_format_comment = {
                'platform': 'youtube',
                'id': comment['id'],
                "campaign_id": campaign.id,
                'message': comment['snippet']['displayMessage'],
                "created_time": comment_time_stamp,
                "customer_id": comment['authorDetails']['channelId'],
                "customer_name": comment['authorDetails']['displayName'],
                "image": comment['authorDetails']['profileImageUrl'],
                "live_chat_id": live_chat_id,
                "categories":service.nlp.classification.classify_comment_v2(texts=[comment['snippet']['displayMessage']])
            }
            try:
                database.lss.campaign_comment.CampaignComment.create(**uni_format_comment, auto_inc=False)
            except Exception:
                continue
            service.channels.campaign.send_comment_data(campaign.id, uni_format_comment)
            service.rq.queue.enqueue_comment_queue(jobs.comment_job_v2.comment_job, campaign.data, user_subscription_data, 'youtube', youtube_channel.data, uni_format_comment, order_codes_mapping)

         

    except Exception :

        if attempts>0:
            capture_youtube_v2(campaign, user_subscription_data, logs, attempts=attempts-1)
        print(traceback.format_exc())


def __update_campaign_silent_count(pymongo_campaign:database.lss.campaign.Campaign):
    
    if pymongo_campaign.data.get('priority',0) >= LOWEST_PRIORITY:
        pymongo_campaign.increment_silent_count(sync=False)
        return

    if pymongo_campaign.data.get('silent_count',0) >= C_VALUE:
        pymongo_campaign.deprioritize(sync=False)
    else:
        pymongo_campaign.increment_silent_count(sync=False)

