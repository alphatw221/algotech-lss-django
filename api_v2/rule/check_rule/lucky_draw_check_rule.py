from api import models
from automation.jobs.crawler_job import crawler_shared_post_job
import lib
import service


class LuckyDrawCheckRule():

    @staticmethod
    def is_draw_type_valid(**kwargs):
        lucky_draw = kwargs.get('lucky_draw')
        campaign = kwargs.get('campaign')
        if lucky_draw.type not in models.campaign.campaign_lucky_draw.TYPE_CHOICES:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_lucky_draw_type')
        if lucky_draw.type in [models.campaign.campaign_lucky_draw.TYPE_LIKE, models.campaign.campaign_lucky_draw.TYPE_POST] and campaign.facebook_campaign.get('post_id', "") == "":
            raise lib.error_handle.error.api_error.ApiVerifyError('draw_like_type_need_connect_to_facebook_post')
        
    @staticmethod
    def is_draw_prize_valid(**kwargs):
        lucky_draw = kwargs.get('lucky_draw')
        prize = lucky_draw.prize
        if prize == {}: 
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_lucky_draw_product')
        
    @staticmethod
    def is_connected_to_any_platform(**kwargs):
        campaign = kwargs.get('campaign')
        # connected_platform = []
        if campaign.facebook_campaign.get("post_id"):
            return
            # connected_platform.append("facebook")
        elif campaign.instagram_campaign.get("live_media_id"):
            return
            # connected_platform.append("instagram")
        elif campaign.youtube_campaign.get("live_video_id"):
            return
        elif campaign.twitch_campaign.get("channel_name"):
            return
        elif campaign.tiktok_campaign.get("username"):
            return
            # connected_platform.append("youtube")

        # if len(connected_platform) == 0:
        raise lib.error_handle.error.api_error.ApiVerifyError('no_any_connected_platforms')
        
        
        # if type not in models.campaign.campaign_lucky_draw.TYPE_CHOICES:
        #     raise lib.error_handle.error.api_error.ApiVerifyError('invalid_lucky_draw_type')
        # elif type == models.campaign.campaign_lucky_draw.TYPE_PRODUCT and data.get('campaign_product', '') == '': 
        #     raise lib.error_handle.error.api_error.ApiVerifyError('invalid_lucky_draw_product')
        
    @staticmethod
    def is_needed_to_start_sharedpost_crawler(**kwargs):
        lucky_draw = kwargs.get('lucky_draw')
        campaign = kwargs.get('campaign')
        username = campaign.facebook_page.username
        post_id = campaign.facebook_campaign.get("post_id", "")
        if not username:
            raise lib.error_handle.error.api_error.ApiVerifyError('missing_username_of_facebook_page')
        
        if lucky_draw.type in [models.campaign.campaign_lucky_draw.TYPE_POST]:
            print("start crawler")
            service.rq.queue.enqueue_general_queue(job=crawler_shared_post_job, lucky_draw_id=lucky_draw.id, facebook_page_username=username, post_id=post_id)
