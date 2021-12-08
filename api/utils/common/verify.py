from backend.api.facebook.user import api_fb_get_me_accounts
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel

platform_dict = {'facebook': FacebookPage,
                 'youtube': YoutubeChannel}


class ApiVerifyError(Exception):
    pass


class Verify():

    @staticmethod
    def is_admin(api_user, platform_name, platform):
        try:
            if platform_name == 'facebook':
                print('in')
                status_code, response = api_fb_get_me_accounts(
                    api_user.facebook_info['token'])
                for item in response['data']:
                    if item['id'] == platform.page_id:
                        return True
                return False
            elif platform_name == 'youtube':
                return True
        except Exception as e:
            return False
        return False

    @staticmethod
    def verify_user(api_user):
        if not api_user:
            raise ApiVerifyError("no user found")
        elif api_user.status != "valid":
            raise ApiVerifyError("not activated user")

    @classmethod
    def get_platform(cls, api_user, platform_name, platform_id):
        if platform_name not in platform_dict:
            raise ApiVerifyError("no platfrom name found")
        if not platform_dict[platform_name].objects.filter(id=platform_id).exists():
            raise ApiVerifyError("no platfrom found")
        platform = platform_dict[platform_name].objects.get(
            id=platform_id)
        if not cls.is_admin(api_user, platform_name, platform):
            raise ApiVerifyError("user is not platform admin")
        return platform

    @staticmethod
    def get_user_subscription(platform):
        user_subscriptions = platform.user_subscriptions.all()
        if not user_subscriptions:
            raise ApiVerifyError("platform not in any user_subscription")
        user_subscription = user_subscriptions[0]
        return user_subscription

    @staticmethod
    def get_campaign(platform, campaign_id):
        if not platform.campaigns.filter(id=campaign_id).exists():
            raise ApiVerifyError("no campaign found")
        campaign = platform.campaigns.get(id=campaign_id)
