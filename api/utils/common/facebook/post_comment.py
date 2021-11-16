from api.models.campaign.campaign import Campaign
from api.utils.api.facebook.post import api_fb_get_post_comments
from api.utils.orm.campaign_comment import get_latest_commented_at, update_or_create_comment

MAX_CONTINUOUS_REQUEST_TIMES = 10


def campaign_facebook_post_capture_comments(campaign: Campaign):
    try:
        page_token = campaign.facebook_page.token
        post_id = campaign.facebook_campaign['post_id']
        if not all([page_token, post_id]):
            return

        return _capture_comments_helper(campaign, page_token, post_id)
    except Exception:
        return


def _capture_comments_helper(campaign: Campaign, page_token: str, post_id: str):
    def _capture_batch_comments(since: int):
        code, data = api_fb_get_post_comments(page_token, post_id, since)
        if code // 100 != 2:
            if 'error' in data:
                _handle_facebook_error(data)
            return

        comments = data.get('data', [])
        _save_comments(comments)
        _update_stats(comments)
        return _get_since(comments)

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

    def _update_stats(comments):
        nonlocal total_comments_captured
        total_comments_captured += len(comments)

    def _get_since(comments):
        if len(comments) <= 1:
            return False  # False is the signal to stop iteration
        return comments[-1]['created_time']

    total_comments_captured = 0
    since = get_latest_commented_at(campaign, 'facebook')
    for _ in range(MAX_CONTINUOUS_REQUEST_TIMES):
        since = _capture_batch_comments(since)
        if not since:
            break

    return f'{campaign.id=} {total_comments_captured=}'
