from django.conf import settings
from service.tiktok._tk_api_caller import TiktokApiCaller, TiktokBusinessApiCaller
import requests

def api_tiktok_get_me(token: str):
    # code, ret = TiktokApiCaller('userinfo/v2/me', bearer_token=token).get()
    # return code, ret
    pass


def api_google_get_userinfo(token: str):
    # code, ret = TiktokApiCaller('oauth2/v2/userinfo', bearer_token=token).get()
    # return code, ret
    pass


def api_tiktok_get_token(code):
    data = {
        "app_id": settings.TIKTOK_APP_ID,
        "secret": settings.TIKTOK_APP_SECRET,
        "auth_code": code
    }
    return TiktokBusinessApiCaller("/open_api/v1.3/oauth2/access_token/", data=data).post()