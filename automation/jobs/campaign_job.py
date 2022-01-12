import os
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE']='lss.settings' #for rq_job
    django.setup()
except Exception:
    pass

from backend.api.facebook.post import api_fb_get_post_comments
from backend.api.instagram.post import api_ig_get_post_comments
from backend.api.instagram.user import api_ig_get_id_from, api_ig_get_profile_picture
from backend.api.youtube.live_chat import api_youtube_get_live_chat_comment
from backend.python_rq.python_rq import comment_queue
from automation.jobs.comment_job import comment_job

from backend.pymongo.mongodb import db,client

def campaign_job(campaign_id):
    try:
        print(f"campaign_id: {campaign_id}\n")
        campaign=db.api_campaign.find_one({"id":campaign_id})
        try:
            if campaign['facebook_page_id']:
                facebook_page=db.api_facebook_page.find_one({"id":campaign['facebook_page_id']})
                capture_facebook(campaign, facebook_page)
        except Exception:
            pass

        try:
            if campaign['youtube_channel_id']:
                youtube_channel = db.api_youtube_channel.find_one({'id': campaign['youtube_channel_id']})
                capture_youtube(campaign, youtube_channel)
        except Exception:
            pass

        try:
            if campaign['instagram_profile_id']:
                instagram_post = db.api_instagram_profile.find_one({'id': int(campaign['instagram_profile_id'])})
                capture_instagram(campaign, instagram_post)
                
        except Exception:
            pass

    except Exception:
        pass


def capture_facebook(campaign, facebook_page):
    page_token=facebook_page['token']
    facebook_campaign=campaign['facebook_campaign']
    post_id=facebook_campaign.get('post_id','')
    since=facebook_campaign.get('comment_capture_since', 1)

    if not page_token or not post_id:
        return

    campaign_products = db.api_campaign_product.find({"campaign_id":campaign['id'], "$or":[ {"type":"product"}, {"type":"product-fast"}]})
    order_codes_mapping={campaign_product['order_code'].lower() : campaign_product
        for campaign_product in campaign_products}


    code, data = api_fb_get_post_comments(page_token, post_id, since)
    print(f"page_token: {page_token}\n")
    print(f"post_id: {post_id}\n")
    print(f"since: {since}\n")
    print(f"code: {code}\n")

    if code // 100 != 2 and 'error' in data and data['error']['type'] in ('GraphMethodException', 'OAuthException'):
        facebook_campaign['post_id'] = ''
        facebook_campaign['remark'] = f'Facebook API error: {data["error"]}'
        db.api_campaign.update_one({'id':campaign['id']},{'$set':{"facebook_campaign", facebook_campaign}})
        return

    comment_capture_since=since
    comments = data.get('data', [])

    print(f"number of comments: {len(comments)}")
    if len(comments) == 1 and comments[0]['created_time'] == since:
        return

    try:
        for comment in comments:
            print(comment['message'])
            if comment['from']['id']==facebook_page['page_id']:
                continue
            uni_format_comment={
                'platform': 'facebook',
                'id': comment['id'],
                "campaign_id":campaign['id'],
                'message': comment['message'],
                "created_time": comment['created_time'], 
                "customer_id": comment['from']['id'], 
                "customer_name": comment['from']['name'], 
                "image": comment['from']['picture']['data']['url']}
            db.api_campaign_comment.insert_one(uni_format_comment)
            comment_queue.enqueue(comment_job,args=(campaign, 'facebook', facebook_page, uni_format_comment, order_codes_mapping), result_ttl=10, failure_ttl=10)
            comment_capture_since=comment['created_time']
    except Exception as e:
        print(e)

    facebook_campaign['comment_capture_since']=comment_capture_since
    db.api_campaign.update_one({'id':campaign['id']},{"$set":{'facebook_campaign':facebook_campaign}})
    

def capture_youtube(campaign, youtube_channel):
    page_token = youtube_channel['page_token']
    youtube_campaign = campaign['youtube_campaign']
    live_chat_id = youtube_campaign['live_chat_id']
    next_page_token = ''
    try: 
        next_page_token = youtube_campaign['next_page_token']
    except:
        pass
    
    if not page_token or not live_chat_id:
        return
    
    campaign_products = db.api_campaign_product.find({"campaign_id":campaign['id'], "$or":[ {"type":"product"}, {"type":"product-fast"}]})
    order_codes_mapping = {campaign_product['order_code'].lower() : campaign_product
        for campaign_product in campaign_products}
    
    if next_page_token != '':
        page_token = next_page_token

    code, data = api_youtube_get_live_chat_comment(page_token, live_chat_id, 100)
    if code // 100 != 2 and 'error' in data:
        youtube_campaign['remark'] = f'Facebook API error: {data["error"]["message"]}'
        db.api_campaign.update_one({'id':campaign['id']},{'$set':{"facebook_campaign", youtube_campaign}})
        return
    
    next_page_token = data['nextPageToken']
    comments = data.get('items', [])
    is_failed, latest_comment_time = False, ''
    try:
        for comment in comments:
            try:
                is_failed = youtube_campaign['is_failed']
                latest_comment_time = youtube_campaign['latest_comment_time']
            except:
                pass
            
            if is_failed == True and comment['snippet']['publishedAt'] > latest_comment_time:
                pass
            else:
                uni_format_comment={
                    'platform': 'youtube',
                    'id': comment['id'],
                    "campaign_id":campaign['id'],
                    'message': comment['snippet']['displayMessage'],
                    "created_time": comment['snippet']['publishedAt'], 
                    "customer_id": comment['snippet']['liveChatId'], 
                    "customer_name": comment['authorDetails']['displayName'], 
                    "image": comment['authorDetails']['profileImageUrl']
                }
                db.api_campaign_comment.insert_one(uni_format_comment)
                #TODO YT comment job

        youtube_campaign['next_page_token'] = next_page_token
        youtube_campaign['is_failed'] = False 
        db.api_campaign.update_one({'id': campaign['id']}, {"$set":{'youtube_campaign': youtube_campaign}})
    except Exception:
        lastest_comment_time = db.api_campaign_comment.find_one({'platform': 'youtube'}, sort=[('created_time', -1)])['created_time']
        youtube_campaign['is_failed'] = True
        youtube_campaign['latest_comment_time'] = lastest_comment_time
        db.api_campaign.update_one({'id': campaign['id']}, {"$set":{'youtube_campaign': youtube_campaign}})
        return


def capture_instagram(campaign, instagram_post):
    page_token = instagram_post['token']
    instagram_campaign = campaign['instagram_campaign']
    post_id = instagram_campaign['live_media_id']

    if not page_token or not post_id:
        return
    
    campaign_products = db.api_campaign_product.find({"campaign_id":campaign['id'], "$or":[ {"type":"product"}, {"type":"product-fast"}]})
    order_codes_mapping={campaign_product['order_code'].lower() : campaign_product
        for campaign_product in campaign_products}
    
    code, data = api_ig_get_post_comments(page_token, post_id)
    if code // 100 != 2 and 'error' in data and data['error']['type'] in ('GraphMethodException', 'OAuthException'):
        instagram_campaign['post_id'] = post_id
        instagram_campaign['remark'] = f'Instagram API error: {data["error"]}'
        db.api_campaign.update_one({'id':campaign['id']},{'$set':{"instagram_campaign", instagram_campaign}})
        return
    
    
    comments = data.get('data', [])
    is_failed, latest_comment_time = False, ''
    try:
        for comment in comments:
            try:
                is_failed = instagram_campaign['is_failed']
                latest_comment_time = instagram_campaign['latest_comment_time']
            except:
                pass
            
            if is_failed == True and comment['timestamp'] > latest_comment_time:
                pass
            else:
                from_info = api_ig_get_id_from(page_token, comment['id'])
                profile_img_url = api_ig_get_profile_picture(page_token, from_info[1]['from']['id'])
                img_url = ''

                if profile_img_url[0] == 400:
                    img_url == ''
                if profile_img_url[0] == 200:
                    img_url = profile_img_url[1]['profile_picture_url']

                uni_format_comment={
                    'platform': 'instagram',
                    'id': comment['id'],
                    "campaign_id":campaign['id'],
                    'message': comment['text'],
                    "created_time": comment['timestamp'], 
                    "customer_id": comment['id'], 
                    "customer_name": from_info[1]['from']['username'], 
                    "image": img_url}
                db.api_campaign_comment.insert_one(uni_format_comment)
            #TODO comment queue job
        instagram_campaign['is_failed'] = False 
        db.api_campaign.update_one({'id': campaign['id']}, {"$set":{'instagram_campaign': instagram_campaign}})
    except Exception:
        lastest_comment_time = db.api_campaign_comment.find_one({'platform': 'instagram'}, sort=[('created_time', -1)])['created_time']
        instagram_campaign['is_failed'] = True
        instagram_campaign['latest_comment_time'] = lastest_comment_time
        db.api_campaign.update_one({'id': campaign['id']}, {"$set":{'instagram_campaign': instagram_campaign}})
        return