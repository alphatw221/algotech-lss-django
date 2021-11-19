from api.models.campaign.campaign import Campaign
from backend.utils.api.facebook.post import api_fb_get_post_comments
from api.utils.orm.campaign_comment import get_latest_commented_at, update_or_create_comment, get_comments_count
from django.conf import settings


class FacebookCaptureCommentError(Exception):
    """Error when capturing Facebook comments."""


def campaign_facebook_post_capture_comments(campaign: Campaign):
    try:
        page_token = campaign.facebook_page.token
        post_id = campaign.facebook_campaign['post_id']
    except Exception:
        raise FacebookCaptureCommentError('Missing page_token or post_id')
    if not page_token or not post_id:
        raise FacebookCaptureCommentError('Missing page_token or post_id')

    try:
        return _capture_comments_helper(campaign, page_token, post_id)
    except FacebookCaptureCommentError as e:
        raise e
    except Exception:
        raise FacebookCaptureCommentError('Module internal error')


def _capture_comments_helper(campaign: Campaign, page_token: str, post_id: str):
    def _capture_comments(since: int):
        code, data = api_fb_get_post_comments(page_token, post_id, since)
        if code // 100 != 2:
            if 'error' in data:
                _handle_facebook_error(data)
            raise FacebookCaptureCommentError('Facebook API error')

        comments = data.get('data', [])
        comments_captured = _save_comments(comments)
        latest_commented_at = _get_latest_commented_at(comments)

        return comments_captured, latest_commented_at

    def _handle_facebook_error(data):
        if data['error']['type'] in ('GraphMethodException', 'OAuthException'):
            campaign.facebook_campaign['post_id'] = ''
            campaign.facebook_campaign['remark'] = f'Facebook API error: {data["error"]}'
            campaign.save()

    def _save_comments(comments):
        for comment in comments:
            update_or_create_comment(campaign, 'facebook', comment['id'], {
                'message': comment['message'],
                'commented_at': comment['created_time'],
                'customer_id': comment['from']['id'],
                'customer_name': comment['from']['name'],
                'image': comment['from']['picture']['data']['url'],
            })
        return len(comments)

    def _get_latest_commented_at(comments):
        if len(comments) <= 1:
            return False  # False means to stop iteration
        return comments[-1]['created_time']

    total_comments_captured = 0
    commented_at = get_latest_commented_at(campaign, 'facebook')
    for _ in range(settings.FACEBOOK_COMMENT_CAPTURING['MAX_CONTINUOUS_REQUEST_TIMES']):
        comments_captured, commented_at = _capture_comments(commented_at)
        total_comments_captured += comments_captured
        if not commented_at:
            break

    total_campaign_comments = get_comments_count(campaign, 'facebook')
    return f'{total_comments_captured=} {total_campaign_comments=}'
