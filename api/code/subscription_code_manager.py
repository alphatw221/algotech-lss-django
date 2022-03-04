from api.code.code_manager import CodeManager
from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from api.models.instagram.instagram_profile import InstagramProfile
from api.models.user.user_subscription import UserSubscription
from api.utils.error_handle.error.api_error import ApiVerifyError
from datetime import datetime

class SubscriptionCodeManager(CodeManager):

    code_key="add_subscription"

    data_format = {
        "user_subscription_id":None,
        "avaliable_count":None,
        "issued_time":None,
        "expired_time":None,
    }

    plarforms = {"facebook":FacebookPage, "youtube":YoutubeChannel, "instagram":InstagramProfile}
    user_subscription_platforms = {"facebook":"facebook_pages", "youtube":"youtube_channels", "instagram":"instagram_profiles"}

    @classmethod
    def generate(cls,user_subscription_id, maximum_usage_count, interval):
        data = cls.data_format.copy()
        data['user_subscription_id']=user_subscription_id
        data['maximum_usage_count']=maximum_usage_count
        data['issued_time']=datetime.now().timestamp()
        data['expired_time']=data['issued_time']+interval
        
        return cls._encode(data)

    
    
    @classmethod
    def execute(cls, code, platform_name, platform_id):

        data = cls._decode(code)

        if data.get('expired_time',1)<datetime.now().timestamp():
            raise ApiVerifyError('code expired') 

        platform = cls.plarforms.get(platform_name).objects.get(id=platform_id)
        user_subscription = UserSubscription.objects.get(id = data.get('user_subscription_id'))

        if not (platform and user_subscription):
            raise ApiVerifyError('no platform or user_subscription found')


        if code in user_subscription.meta_code and user_subscription.meta_code[code]>=data.get("maximum_usage_count"):
            raise ApiVerifyError('code reach maxium usage count')

        
        getattr(user_subscription, cls.user_subscription_platforms.get(platform_name)).add(platform)
        
        if code in user_subscription.meta_code:
            user_subscription.meta_code[code]+=1
        else:
            user_subscription.meta_code[code]=1
        user_subscription.save()