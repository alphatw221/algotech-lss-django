# from django.conf import settings
# from api.models.campaign.campaign import Campaign
# from api.utils.orm.campaign_comment import (get_comments_count,
#                                             get_latest_commented_at,
#                                             update_or_create_comment)
# from platform import platform


import os
os.environ['DJANGO_SETTINGS_MODULE']='lss.settings' #for rq_job
from backend.api.facebook.post import api_fb_get_post_comments
from backend.python_rq.python_rq import comment_queue
from automation.jobs.comment_job import comment_job

from backend.pymongo.mongodb import db,client

class FacebookCaptureCommentError(Exception):
    """Error when capturing Facebook comments."""


def campaign_job(campaign_id):
    print(campaign_id)
    campaign=db.api_campaign.find_one({"id":campaign_id})

    if campaign['facebook_page_id']:
        facebook_page=db.api_facebook_page.find_one({"id":campaign['facebook_page_id']})
        capture_facebook(campaign, facebook_page)
    if campaign['youtube_channel_id']:
        pass
    if campaign['instagram_profile_id']:
        pass


def capture_facebook(campaign, facebook_page):
    page_token=facebook_page['token']
    facebook_campaign=campaign['facebook_campaign']
    post_id=facebook_campaign['post_id']
    since=facebook_campaign['comment_capture_since'] if facebook_campaign['comment_capture_since'] else 0

    campaign_products = db.api_campaign_product.find({"campaign_id":campaign['id']})
    order_codes_mapping={campaign_product['order_code'].lower() : campaign_product
        for campaign_product in campaign_products}


    code, data = api_fb_get_post_comments(page_token, post_id, since)
    print(f"page_token: {page_token}\n")
    print(f"post_id: {post_id}\n")
    print(f"since: {since}\n")
    print(f"code: {code}\n")
    # print(f"data: {data}\n")
    if code // 100 != 2:
        return
        pass # handle error

    comment_capture_since=since
    comments = data.get('data', [])
    try:
        for comment in comments:
            if comment['from']['id']==facebook_page['page_id']:
                continue
            uni_format_comment={}
            uni_format_comment['platform']='facebook'
            uni_format_comment['id']=comment['id']
            uni_format_comment['message']=comment['message']
            uni_format_comment['created_time']=comment['created_time']
            uni_format_comment['customer_id']=comment['from']['id']
            uni_format_comment['customer_name']=comment['from']['name']
            uni_format_comment['image']=comment['from']['picture']['data']['url']
            db.api_campaign_comment.insert_one({"platform":'facebook',
                "campaign_id":campaign['id'],
                "comment_id":uni_format_comment['id'],
                "message": uni_format_comment['message'],
                "commented_at": uni_format_comment['created_time'],
                "customer_id": uni_format_comment['customer_id'],
                "customer_name": uni_format_comment['customer_name'],
                "image":uni_format_comment['image']})
            comment_queue.enqueue(comment_job,args=(campaign, 'facebook', facebook_page, uni_format_comment, order_codes_mapping), result_ttl=10, failure_ttl=10)
            comment_capture_since=comment['created_time']
    except Exception as e:
        print(e)
    if comments:
        facebook_campaign['comment_capture_since']=comment_capture_since
        db.api_campaign.update_one({'id':campaign['id']},{"$set":{'facebook_campaign':facebook_campaign}})
    

def capture_youtube():
    pass

def capture_instagram():
    pass