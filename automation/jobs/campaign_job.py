from django.conf import settings
from api.models.campaign.campaign import Campaign
from api.utils.orm.campaign_comment import (get_comments_count,
                                            get_latest_commented_at,
                                            update_or_create_comment)
from backend.api.facebook.post import api_fb_get_post_comments

from backend.python_rq.python_rq import comment_queue
from automation.jobs.comment_job import comment_job

from backend.pymongo.mongodb import db,client

class FacebookCaptureCommentError(Exception):
    """Error when capturing Facebook comments."""


def campaign_job(campaign_id):

    print(campaign_id)

    for i in range(5):
        comment_queue.enqueue(comment_job,args=(f"{campaign_id} - {i}"))
    # campaign=Campaign.objects.get(id=campaign_id)
    # try:
    #     page_token = campaign.facebook_page.token
    #     post_id = campaign.facebook_campaign['post_id']
    # except Exception:
    #     raise FacebookCaptureCommentError('Missing page_token or post_id')
    # if not page_token or not post_id:
    #     raise FacebookCaptureCommentError('Missing page_token or post_id')

    # try:
    #     return capture_comments_helper(campaign, page_token, post_id)
    # except FacebookCaptureCommentError:
    #     raise
    # except Exception:
    #     raise FacebookCaptureCommentError('Module internal error')

# def capture_comments_helper(campaign: Campaign, page_token: str, post_id: str):
#     def _capture_comments(since: int):
#         code, data = api_fb_get_post_comments(page_token, post_id, since)
#         if code // 100 != 2:
#             if 'error' in data:
#                 _handle_facebook_error(data)
#             raise FacebookCaptureCommentError('Facebook API error')

#         comments = data.get('data', [])
#         comments_captured = _save_and_enqueue_comments(comments)
#         latest_commented_at = _get_latest_commented_at(comments)

#         return comments_captured, latest_commented_at

#     def _handle_facebook_error(data):
#         if data['error']['type'] in ('GraphMethodException', 'OAuthException'):
#             campaign.facebook_campaign['post_id'] = ''
#             campaign.facebook_campaign['remark'] = f'Facebook API error: {data["error"]}'
#             campaign.save()

#     def _save_and_enqueue_comments(comments):
#         order_codes_mapping={}
#         if campaign.enable_order_code:
#             order_codes_mapping={campaign_product.order_code.lower() : campaign_product
#                 for campaign_product in campaign.products}

#         for comment in comments:
#             campaign_comment, _=update_or_create_comment(campaign, 'facebook', comment['id'], {
#                 'message': comment['message'],
#                 'commented_at': comment['created_time'],
#                 'customer_id': comment['from']['id'],
#                 'customer_name': comment['from']['name'],
#                 'image': comment['from']['picture']['data']['url'],
#             })
#             comment_queue.enqueue(comment_job,args=(campaign.id,campaign_comment.id,order_codes_mapping))
#         return len(comments)

#     def _get_latest_commented_at(comments):
#         if len(comments) <= 1:
#             return False  # False means to stop iteration
#         return comments[-1]['created_time']

#     total_comments_captured = 0
#     commented_at = get_latest_commented_at(campaign, 'facebook')
#     for _ in range(settings.FACEBOOK_COMMENT_CAPTURING['MAX_CONTINUOUS_REQUEST_TIMES']):
#         comments_captured, commented_at = _capture_comments(commented_at)
#         total_comments_captured += comments_captured
#         if not commented_at:
#             break

#     total_campaign_comments = get_comments_count(campaign, 'facebook')
#     return f'{total_comments_captured=} {total_campaign_comments=}'