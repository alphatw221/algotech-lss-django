import os
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE']='lss.settings' #for rq_job
    django.setup()
except Exception:
    pass

from backend.api.facebook.post import api_fb_get_post_comments
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
                pass
        except Exception:
            pass

        try:
            if campaign['instagram_profile_id']:
                pass
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

    if len(comments) == 1 and comments[0]['created_time'] == since:
        return

    try:
        for comment in comments:
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
    except Exception:
        facebook_campaign['comment_capture_since']=comment_capture_since
        db.api_campaign.update_one({'id':campaign['id']},{"$set":{'facebook_campaign':facebook_campaign}})
    

def capture_youtube():
    pass

def capture_instagram():
    pass