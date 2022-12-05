from ast import Param
import json
from six import string_types
from urllib.parse import urlencode, urlunparse
from django.conf import settings
from service.tiktok._tk_api_caller import TiktokApiCaller, TiktokBusinessApiCaller
import requests

def api_tiktok_get_me(token: str):
    # code, ret = TiktokApiCaller('userinfo/v2/me', bearer_token=token).get()
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