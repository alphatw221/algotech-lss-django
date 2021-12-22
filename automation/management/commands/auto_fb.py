from datetime import datetime
import pendulum
from automation.utils.timeloop import time_loop
from backend.campaign.campaign.manager import CampaignManager
from backend.comment_catching.facebook.post_comment import \
    campaign_facebook_post_capture_comments
from django.conf import settings
from django.core.management.base import BaseCommand
from backend.pymongo.mongodb import db,client


from api.models.campaign.campaign import Campaign
from api.utils.orm.campaign_comment import (get_comments_count,
                                            get_latest_commented_at,
                                            update_or_create_comment)
from backend.api.facebook.post import api_fb_get_post_comments
from django.conf import settings

class FacebookCaptureCommentError(Exception):
    """Error when capturing Facebook comments."""

class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # self.campaign_facebook_capture_comments()
        self.test()

    @time_loop(settings.FACEBOOK_COMMENT_CAPTURING['REST_INTERVAL_SECONDS'])
    def campaign_facebook_capture_comments(self):
        self.stdout.write(self.style.SUCCESS(
            f'{pendulum.now()} - Auto Facebook Comment Module'))

        for campaign in CampaignManager.get_ordering_campaigns():
            try:
                result = campaign_facebook_post_capture_comments(campaign)
            except Exception as e:
                result = e
            print(f'{pendulum.now()} - {campaign.title=} {campaign.id=} - {result=}')


    @time_loop(settings.FACEBOOK_COMMENT_CAPTURING['REST_INTERVAL_SECONDS'])
    def test(self):
        self.stdout.write(self.style.SUCCESS(
            f'{pendulum.now()} - test Module'))

        api_campaigns=db.api_campaign.find({"start_at":{"$lt":datetime.utcnow()}, "end_at":{"$gt":datetime.utcnow()}})
        for api_campaign in api_campaigns:
            #get campaign comment:
            
            try:
                api_facebook_page=db.api_facebook_page.find_one({"id":api_campaign['facebook_page_id']})
                page_token=api_facebook_page['token']
                print(page_token)
                post_id = api_campaign['facebook_campaign']['post_id']
                print(post_id)
            except Exception:
                raise FacebookCaptureCommentError('Missing page_token or post_id')
            if not page_token or not post_id:
                raise FacebookCaptureCommentError('Missing page_token or post_id')

            try:
                return _capture_comments_helper(api_campaign, page_token, post_id)
            except FacebookCaptureCommentError:
                raise
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
        pass

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
