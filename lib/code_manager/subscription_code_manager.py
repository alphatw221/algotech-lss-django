from api import models
from datetime import datetime

from .code_manager import CodeManager
from lib import error_handle
class SubscriptionCodeManager(CodeManager):

    code_key="add_subscription"

    data_format = {
        "user_subscription_id":None,
        "maximum_usage_count":None,
        "issued_time":None,
        "expired_time":None,
    }

    plarforms = {"facebook": models.facebook.facebook_page.FacebookPage, "youtube": models.youtube.youtube_channel.YoutubeChannel, "instagram":models.instagram.instagram_profile.InstagramProfile}
    user_subscription_platforms = {"facebook": "facebook_pages", "youtube": "youtube_channels", "instagram": "instagram_profiles"}

    @classmethod
    def generate(cls,user_subscription_id, maximum_usage_count=1, interval=3000):
        data = cls.data_format.copy()
        data['user_subscription_id']=user_subscription_id
        data['maximum_usage_count']=maximum_usage_count
        data['issued_time']=datetime.now().timestamp()
        data['expired_time']=data['issued_time']+interval
        print(data)
        
        return cls._encode(data)

    
    
    @classmethod
    def execute(cls, code, platform_name, platform_id):

        data = cls._decode(code)

        if float(data.get('expired_time', 1)) <datetime.now().timestamp():
            raise error_handle.error.api_error.ApiVerifyError('code expired') 

        platform = cls.plarforms.get(platform_name).objects.get(id=platform_id)
        user_subscription = models.user.user_subscription.UserSubscription.objects.get(id = data.get('user_subscription_id'))

        if not (platform and user_subscription):
            raise error_handle.error.api_error.ApiVerifyError('no platform or user_subscription found')


        if code in user_subscription.meta_code and user_subscription.meta_code[code]>=data.get("maximum_usage_count"):
            raise error_handle.error.api_error.ApiVerifyError('code reach maxium usage count')

        getattr(user_subscription, cls.user_subscription_platforms.get(platform_name)).add(platform)
        
        if code in user_subscription.meta_code:
            user_subscription.meta_code[code]+=1
        else:
            user_subscription.meta_code[code]=1
        user_subscription.save()
        return models.user.user_subscription.UserSubscriptionSerializer(user_subscription).data