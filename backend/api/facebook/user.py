from backend.api.facebook._fb_api_caller import FacebookApiCaller
from django.conf import settings


def api_fb_get_me(token: str):
    ret = FacebookApiCaller('me', bearer_token=token).get()
    return ret

def api_fb_get_me_login(token: str):
    params = {
        'fields': "id,name,email,picture"
    }
    ret = FacebookApiCaller('me', bearer_token=token, params=params).get()
    return ret
    
def api_fb_get_id(token: str, user_or_page_id: str):
    ret = FacebookApiCaller(user_or_page_id, bearer_token=token).get()
    return ret


def api_fb_get_me_accounts(user_token: str):
    params = {"fields":"id,name,access_token"}
    ret = FacebookApiCaller('/v13.0/me/accounts',
                            bearer_token=user_token,params=params).get()
    return ret


def api_fb_get_accounts_from_user(user_token: str, user_id: str):
    ret = FacebookApiCaller(f'{user_id}/accounts',
                            bearer_token=user_token,).get()
    return ret


def api_fb_get_page_token_from_user(user_token: str, page_id: str):
    ret = FacebookApiCaller(page_id, bearer_token=user_token,
                            params={"fields": "access_token"}).get()
    return ret


def api_fb_get_long_lived_token(token: str):
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': settings.FACEBOOK_APP_CREDS['app_id'],
        'client_secret': settings.FACEBOOK_APP_CREDS['app_secret'],
        'fb_exchange_token': token,
    }
    ret = FacebookApiCaller(f'oauth/access_token',
                            params=params).get()
    return ret
