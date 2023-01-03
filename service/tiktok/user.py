from ast import Param
import json
from six import string_types
from urllib.parse import urlencode, urlunparse
from django.conf import settings
from service.tiktok._tk_api_caller import TiktokAdsApiCaller, TiktokBusinessApiCaller, TiktokApiCaller, load_response
import requests

def api_tiktok_get_me(token: str):
    # code, ret = TiktokAdsApiCaller('userinfo/v2/me', bearer_token=token).get()
    # return code, ret
    pass


def api_tiktok_advertiser_info(token: str, advertiser_ids: str):
    headers = {
        "Access-Token": token,
    }

    params = {
        "advertiser_ids": json.dumps(advertiser_ids),
        "fields": '["telephone_number","name","advertiser_id","role","email","country"]',
        "access_token": token
    }

    code, ret = TiktokBusinessApiCaller('open_api/v1.3/advertiser/info', headers=headers, params=params).get()
    return code, ret


def api_tiktok_get_token(code):
    data = {
        "app_id": settings.TIKTOK_APP_ID,
        "secret": settings.TIKTOK_APP_SECRET,
        "auth_code": code
    }
    return TiktokBusinessApiCaller("open_api/v1.3/oauth2/access_token/", data=data).post()


def get_user_token_with_code(code):
    params = {
        'client_key':settings.TIKTOK_CLIENT_KEY,
        'client_secret':settings.TIKTOK_CLIENT_SECRET,
        'code':code,
        'grant_type':'authorization_code'
    }
    res = requests.post(TiktokApiCaller.domain_url+'/oauth/access_token/',params=params)
    return load_response(res)

def get_user_info(token, fields:str):

    headers = {
        'Authorization':f'Bearer {token}'
    }
    params = {'fields':fields}
    res = requests.get('https://open.tiktokapis.com'+'/v2/user/info/', headers=headers, params=params)

    return load_response(res)