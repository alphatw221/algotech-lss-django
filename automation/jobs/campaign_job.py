import os
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lss.settings'  # for rq_job
    django.setup()
except Exception:
    pass

from backend.api.google.user import api_google_post_refresh_token
from backend.api.facebook.post import api_fb_get_post_comments
from backend.api.instagram.post import api_ig_get_post_comments, api_ig_get_after_post_comments
from backend.api.instagram.user import api_ig_get_id_from, api_ig_get_profile_picture
from backend.api.youtube.live_chat import api_youtube_get_live_chat_comment_with_access_token, api_youtube_get_live_chat_comment_with_api_key
from backend.python_rq.python_rq import comment_queue
from automation.jobs.comment_job import comment_job

from backend.pymongo.mongodb import db, client
import requests
import time
from datetime import datetime
from dateutil import parser
from backend.api.youtube.viedo import api_youtube_get_video_info_with_access_token, api_youtube_get_video_info_with_api_key
from api.utils.error_handle.error_handler.campaign_job_error_handler import campaign_job_error_handler
from api.utils.error_handle.error_handler.capture_platform_error_handler import capture_platform_error_handler

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

@campaign_job_error_handler
def campaign_job(campaign_id):

    print(f"campaign_id: {campaign_id}")
    campaign = db.api_campaign.find_one({"id": campaign_id})
    print("-------------------------------------------------------------------------")
    print("Facebook:\n")
    capture_facebook(campaign)
    print("-------------------------------------------------------------------------")
    print("Youtube:\n")
    capture_youtube(campaign)
    print("-------------------------------------------------------------------------")
    print("Instagram:\n")
    capture_instagram(campaign)
    print("-------------------------------------------------------------------------")

@capture_platform_error_handler
def capture_facebook(campaign):

    if not campaign['facebook_page_id']:
        return

    facebook_page = db.api_facebook_page.find_one(
        {"id": campaign['facebook_page_id']})

    page_token = facebook_page['token']
    facebook_campaign = campaign['facebook_campaign']
    post_id = facebook_campaign.get('post_id', '')
    since = facebook_campaign.get('comment_capture_since', 1)

    if not page_token or not post_id:
        return

    # campaign_products = db.api_campaign_product.find(
    #     {"campaign_id": campaign['id'], "$or": [{"type": "product"}, {"type": "product-fast"}]})
    # order_codes_mapping = {campaign_product['order_code'].lower(): campaign_product
    #                        for campaign_product in campaign_products}
    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign['id'])

    code, data = api_fb_get_post_comments(page_token, post_id, since)
    print(f"post_id: {post_id}")
    print(f"since: {since}")
    print(f"code: {code}")

    if code // 100 != 2 and 'error' in data and data['error']['type'] in ('GraphMethodException', 'OAuthException'):
        facebook_campaign['post_id'] = ''
        facebook_campaign['remark'] = f'Facebook API error: {data["error"]}'
        db.api_campaign.update_one({'id': campaign['id']}, {
                                   '$set': {"facebook_campaign", facebook_campaign}})
        return

    comment_capture_since = since
    comments = data.get('data', [])

    if comments and int(comments[-1]['created_time']) == since:
        print(f"number of comments: {0}")
        return

    print(f"number of comments: {len(comments)}")
    try:
        for comment in comments:
            print(comment['message'])
            if comment['from']['id'] == facebook_page['page_id']:
                comment_capture_since = comment['created_time']
                continue
            uni_format_comment = {
                'platform': 'facebook',
                'id': comment['id'],
                "campaign_id": campaign['id'],
                'message': comment['message'],
                "created_time": comment['created_time'],
                "customer_id": comment['from']['id'],
                "customer_name": comment['from']['name'],
                "image": comment['from']['picture']['data']['url']}
            db.api_campaign_comment.insert_one(uni_format_comment)
            comment_queue.enqueue(comment_job, args=(campaign, 'facebook', facebook_page,
                                  uni_format_comment, order_codes_mapping), result_ttl=10, failure_ttl=10)
            comment_capture_since = comment['created_time']
    except Exception as e:
        print(e)

    facebook_campaign['comment_capture_since'] = comment_capture_since
    db.api_campaign.update_one({'id': campaign['id']}, {
                               "$set": {'facebook_campaign': facebook_campaign}})

@capture_platform_error_handler
def capture_youtube(campaign):

    # if not campaign['youtube_channel_id']:
    #     return

    youtube_channel = db.api_youtube_channel.find_one(
                {'id': campaign['youtube_channel_id']})
    # token = youtube_channel['token']

    youtube_campaign = campaign['youtube_campaign']
    access_token = youtube_campaign.get('access_token')
    refresh_token = youtube_campaign.get('refresh_token')
    

    if not access_token or not refresh_token:
        print("need both access_token and refresh_token")
        return


    live_chat_id = youtube_campaign.get('live_chat_id')
    if not live_chat_id:
        live_video_id = youtube_campaign.get('live_video_id')
        if not live_video_id:
            print('no live_video_id')
            return
        code, data = api_youtube_get_video_info_with_api_key(live_video_id)
        # code, data = api_youtube_get_video_info_with_access_token(access_token, live_video_id)
        if code // 100 != 2:

            print("video info error")
            print(data)
            return
        items = data.get("items")
        if not items:
            print("no items")
            return
        liveStreamingDetails = items[0].get('liveStreamingDetails')
        if not liveStreamingDetails:
            print("no liveStreamingDetails")
            return
        live_chat_id = liveStreamingDetails.get('activeLiveChatId')
        youtube_campaign['live_chat_id'] = live_chat_id

    next_page_token = youtube_campaign.get('next_page_token', "")

    if not access_token or not live_chat_id:
        return

    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign['id'])

    # code, data = api_youtube_get_live_chat_comment_with_api_key(
    #     next_page_token, live_chat_id, 100)
    code, data = api_youtube_get_live_chat_comment_with_access_token(access_token, next_page_token, live_chat_id, 100)

    print(f"live_chat_id: {live_chat_id}")
    print(f"next_page_token: {next_page_token}")
    print(f"code: {code}")

    if code // 100 != 2 and 'error' in data:
        youtube_campaign['remark'] = f'Facebook API error: {data["error"]["message"]}'
        db.api_campaign.update_one({'id': campaign['id']}, {
                                   '$set': {"youtube_campaign", youtube_campaign}})
        return

    next_page_token = data['nextPageToken']
    comments = data.get('items', [])
    print(f"number of comments: {len(comments)}")

    if not comments:
        return

    is_failed = youtube_campaign.get('is_failed')
    latest_comment_time = youtube_campaign.get('latest_comment_time', 1)

    try:
        for comment in comments:
            print(comment['snippet']['displayMessage'])

            comment_time_stamp = parser.parse(
                comment['snippet']['publishedAt']).timestamp()

            # print(f"comment_time_stamp: {comment_time_stamp}")
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
                "live_chat_id": live_chat_id
            }
            db.api_campaign_comment.insert_one(uni_format_comment)

            comment_queue.enqueue(comment_job, args=(campaign, 'youtube', youtube_channel,
                                                     uni_format_comment, order_codes_mapping), result_ttl=10, failure_ttl=10)

        youtube_campaign['next_page_token'] = data.get('nextPageToken', "")
        youtube_campaign['latest_comment_time'] = parser.parse(
            comments[-1]['snippet']['publishedAt']).timestamp()
        youtube_campaign['is_failed'] = False

        last_refresh_timestamp = youtube_campaign.get('last_refresh_timestamp',1)
        now_timestamp = datetime.timestamp(datetime.now())
        if last_refresh_timestamp+3000 <= now_timestamp:
            #refresh_token
            print("refreshing token...")
            response = requests.post(
            url="https://accounts.google.com/o/oauth2/token",
            data={
                "client_id": "536277208137-okgj3vg6tskek5eg6r62jis5didrhfc3.apps.googleusercontent.com",  #TODO keep it to settings
                "client_secret": "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",                                 #TODO keep it to settings
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            },)

            code, refresh_token_response = response.status_code, response.json()
            # code, refresh_token_response = api_google_post_refresh_token(refresh_token)
            print(f"refresh status :{code}")
            print(f"refresh data: {refresh_token_response}")
            if code // 100 != 2:
                del youtube_campaign['refresh_token']
            else:
                youtube_campaign['access_token'] = refresh_token_response.get('access_token')
                youtube_campaign['last_refresh_timestamp'] = now_timestamp

        db.api_campaign.update_one({'id': campaign['id']}, {
                                   "$set": {'youtube_campaign': youtube_campaign}})
    except Exception as e:
        print(e)
        latest_campaign_comment = db.api_campaign_comment.find_one(
            {'platform': 'youtube', 'campaign_id': campaign['id']}, sort=[('created_time', -1)])
        youtube_campaign['is_failed'] = True
        youtube_campaign['latest_comment_time'] = latest_campaign_comment['created_time'] if latest_campaign_comment else 1
        db.api_campaign.update_one({'id': campaign['id']}, {
                                   "$set": {'youtube_campaign': youtube_campaign}})
        return

@capture_platform_error_handler
def capture_instagram(campaign):

    if not campaign['instagram_profile_id']:
        return

    instagram_post = db.api_instagram_profile.find_one(
        {'id': int(campaign['instagram_profile_id'])})

    page_token = instagram_post['token']
    instagram_campaign = campaign['instagram_campaign']
    post_id = instagram_campaign['live_media_id']
    since, page_after, page_after_index = '', '', 0
    try:
        since = instagram_campaign['last_create']
    except:
        since = ''
    try:
        page_after = instagram_campaign['page_after']
        page_after_index = instagram_campaign['page_after_index']
    except:
        page_after = ''
        page_after_index = 0
    if not page_token or not post_id:
        return

    # campaign_products = db.api_campaign_product.find(
    #     {"campaign_id": campaign['id'], "$or": [{"type": "product"}, {"type": "product-fast"}]})
    # order_codes_mapping = {campaign_product['order_code'].lower(): campaign_product
    #                        for campaign_product in campaign_products}
    order_codes_mapping = OrderCodesMappingSingleton.get_mapping(campaign['id'])
    
    code, data = '', ''
    if page_after == '':
        code, data = api_ig_get_post_comments(page_token, post_id)
    else:
        code, data = api_ig_get_after_post_comments(
            page_token, post_id, page_after)

    print(f"live_media_id  : {post_id}")
    print(f"code: {code}")

    if code // 100 != 2 and 'error' in data and data['error']['type'] in ('GraphMethodException', 'OAuthException'):
        instagram_campaign['post_id'] = post_id
        instagram_campaign['remark'] = f'Instagram API error: {data["error"]}'
        db.api_campaign.update_one({'id': campaign['id']}, {
                                   '$set': {"instagram_campaign", instagram_campaign}})
        return

    comments = data.get('data', [])
    try:
        page_after = data['paging']['cursors']['after']
    except:
        pass
    print(f"number of comments: {len(comments)}")
    is_failed, latest_comment_time = False, ''
    try:
        created_at = ''
        count = 0
        # for i in range(page_after_index, len(comments)): 
        #     comment = comments[i]
        for comment in comments:
            count += 1
            if page_after_index > count:
                continue
            else:
                if count == 1:
                    created_at = comment['timestamp']
                try:
                    is_failed = instagram_campaign['is_failed']
                    latest_comment_time = instagram_campaign['latest_comment_time']
                except:
                    pass

                if is_failed == True and comment['timestamp'] > latest_comment_time:
                    pass
                else:
                    from_info = api_ig_get_id_from(page_token, comment['id'])
                    profile_img_url = api_ig_get_profile_picture(
                        page_token, from_info[1]['from']['id'])
                    img_url = ''

                    if profile_img_url[0] == 400:
                        img_url == ''
                    if profile_img_url[0] == 200:
                        img_url = profile_img_url[1]['profile_picture_url']
                    if (since < comment['timestamp']):
                        uni_format_comment = {
                            'platform': 'instagram',
                            'id': comment['id'],
                            "campaign_id": campaign['id'],
                            'message': comment['text'],
                            "created_time": comment['timestamp'],
                            # "customer_id": comment['id'],
                            "customer_id": from_info[1]['from']['username'],
                            "customer_name": from_info[1]['from']['username'],
                            "image": img_url}
                        db.api_campaign_comment.insert_one(uni_format_comment)
                        comment_queue.enqueue(comment_job, args=(campaign, 'instagram', instagram_post,
                                                                 uni_format_comment, order_codes_mapping), result_ttl=10, failure_ttl=10)
                    else:
                        continue
                page_after_index = count
        instagram_campaign['is_failed'] = False
        instagram_campaign['last_create'] = created_at
        instagram_campaign['page_after'] = page_after
        instagram_campaign['page_after_index'] = page_after_index
        db.api_campaign.update_one({'id': campaign['id']}, {
            "$set": {'instagram_campaign': instagram_campaign}})
    except Exception:
        lastest_comment_time = db.api_campaign_comment.find_one(
            {'platform': 'instagram'}, sort=[('created_time', -1)])['created_time']
        instagram_campaign['is_failed'] = True
        instagram_campaign['latest_comment_time'] = lastest_comment_time
        db.api_campaign.update_one({'id': campaign['id']}, {
                                   "$set": {'instagram_campaign': instagram_campaign}})
        return
