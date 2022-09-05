from api import models
import lib


class LuckyDrawCheckRule():

    @staticmethod
    def is_draw_type_valid(**kwargs):
        type = kwargs.get('type')
        campaign = kwargs.get('campaign')
        if type not in models.campaign.campaign_lucky_draw.TYPE_CHOICES:
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_lucky_draw_type')
        if type in [models.campaign.campaign_lucky_draw.TYPE_LIKE, models.campaign.campaign_lucky_draw.TYPE_POST] and campaign.facebook_campaign.get('post_id', "") == "":
            raise lib.error_handle.error.api_error.ApiVerifyError('draw_like_type_need_connect_to_facebook_post')
        
    @staticmethod
    def is_draw_prize_valid(**kwargs):
        prize = kwargs.get('prize')
        print(prize)
        if prize == {}: 
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid_lucky_draw_product')
        
    @staticmethod
    def is_connected_to_any_platform(**kwargs):
        campaign = kwargs.get('campaign')
        connected_platform = []
        if campaign.facebook_campaign.get("post_id"):
            connected_platform.append("facebook")
        elif campaign.instagram_campaign.get("live_media_id"):
            connected_platform.append("instagram")
        elif campaign.youtube_campaign.get("live_video_id"):
            connected_platform.append("youtube")

        if len(connected_platform) == 0:
            raise lib.error_handle.error.api_error.ApiVerifyError('no_any_connected_platforms')
        
        
        # if type not in models.campaign.campaign_lucky_draw.TYPE_CHOICES:
        #     raise lib.error_handle.error.api_error.ApiVerifyError('invalid_lucky_draw_type')
        # elif type == models.campaign.campaign_lucky_draw.TYPE_PRODUCT and data.get('campaign_product', '') == '': 
        #     raise lib.error_handle.error.api_error.ApiVerifyError('invalid_lucky_draw_product')