from ..facebook._fb_api_caller import FacebookApiCaller, InstagramApiCaller
from django.conf import settings


def get_user_content(token: str, user_id: str):
    params = {
        'fields': 'id,username'
    }
    ret = FacebookApiCaller(user_id, bearer_token=token, params=params).get()
    return ret


def get_bussiness_id(token: str):
    params = {
        'fields': 'instagram_business_account'
    }
    ret = FacebookApiCaller('me', bearer_token=token, params=params).get()
    return ret


def get_id_from(token: str, post_id: str):
    params = {
        'fields': 'from'
    }
    ret = FacebookApiCaller(post_id, bearer_token=token, params=params).get()
    return ret


def get_profile_picture(token: str, user_id: str):
    params = {
        'fields': 'profile_pic'
    }
    ret = FacebookApiCaller(user_id, bearer_token=token, params=params).get()
    return ret


def get_long_lived_token(token: str):
    params = {
        'grant_type': 'ig_exchange_token',
        'client_secret': settings.FACEBOOK_APP_CREDS['app_secret'],
        'access_token': token,
    }
    ret = InstagramApiCaller(f'oauth/access_token',
                             params=params).get()
    return ret

