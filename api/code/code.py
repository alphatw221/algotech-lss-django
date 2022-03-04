from django.conf import settings
from datetime import datetime

from cryptography.fernet import Fernet
class CodeManager():

    code_key=""

    data_format = {}

    _fernet = Fernet(settings.FERNET_KEY.encode())

    @classmethod
    def _encode(cls, data):

        data["code_key"]=cls.code_key
        data["secret_key"]=settings.FERNET_KEY

        message_string = ""
        for _, value in data.items():
            message_string+=str(value)+"|"
        return cls._fernet.encrypt(message_string[:-1].encode()).decode()

    @classmethod
    def _decode(cls, code):

        message_string = cls._fernet.decrypt(code.encode()).decode()
        print(message_string)
        parameters = message_string.split('|')

        data = cls.data_format.copy()
        if len(parameters) != len(data)+2:
            raise ApiVerifyError('subscription code not valid')
        
        if parameters[-2] != cls.code_key or parameters[-1] != settings.FERNET_KEY:
            raise ApiVerifyError('subscription code not valid')

        for i ,(key, _) in enumerate(data.items()):
            data[key] = parameters[i]

        return data

    @classmethod
    def generate(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def execute(cls, *args, **kwargs):
        raise NotImplementedError



from api.models.facebook.facebook_page import FacebookPage
from api.models.youtube.youtube_channel import YoutubeChannel
from api.models.instagram.instagram_profile import InstagramProfile
from api.models.user.user_subscription import UserSubscription
from api.utils.error_handle.error.api_error import ApiVerifyError




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
    def generate(cls,user_subscription_id, avaliable_count, interval):
        data = cls.data_format.copy()
        data['user_subscription_id']=user_subscription_id
        data['avaliable_count']=avaliable_count
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

        meta = user_subscription.meta.copy()
        code_usage = meta.get('code_usage',{})

        
        getattr(user_subscription, cls.user_subscription_platforms.get(platform_name)).add(platform)
        

