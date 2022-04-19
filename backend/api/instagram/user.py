from backend.api.facebook._fb_api_caller import FacebookApiCaller, InstagramApiCaller
from django.conf import settings


def api_ig_get_user_content(token: str, user_id: str):
    params = {
        'fields': 'id,username'
    }
    ret = FacebookApiCaller(user_id, bearer_token=token, params=params).get()
    return ret


def api_ig_get_bussiness_id(token: str):
    params = {
        'fields': 'instagram_business_account'
    }
    ret = FacebookApiCaller('me', bearer_token=token, params=params).get()
    return ret


def api_ig_get_id_from(token: str, post_id: str):
    params = {
        'fields': 'from'
    }
    ret = FacebookApiCaller(post_id, bearer_token=token, params=params).get()
    return ret


def api_ig_get_profile_picture(token: str, user_id: str):
    params = {
        'fields': 'profile_picture_url'
    }
    ret = FacebookApiCaller(user_id, bearer_token=token, params=params).get()
    return ret


def api_ig_get_long_lived_token(token: str):
    params = {
        'grant_type': 'ig_exchange_token',
        'client_secret': settings.FACEBOOK_APP_CREDS['app_secret'],
        'access_token': token,
    }
    ret = InstagramApiCaller(f'oauth/access_token',
                             params=params).get()
    return ret

