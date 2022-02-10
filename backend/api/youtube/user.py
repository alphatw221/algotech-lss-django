from backend.api.facebook._fb_api_caller import FacebookApiCaller
from django.conf import settings

from backend.api.youtube._youtube_api_caller import GOOGLE_ApiCaller


def api_google_get_me(token: str):
    code, ret = GOOGLE_ApiCaller('userinfo/v2/me', bearer_token=token).get()
    return code, ret

# def api_yt_get_me_login(token: str):
#     params = {
#         'fields': "id,name,email,picture"
#     }
#     ret = FacebookApiCaller('me', bearer_token=token, params=params).get()
#     return ret
#
# def api_yt_get_id(token: str, user_or_page_id: str):
#     ret = FacebookApiCaller(user_or_page_id, bearer_token=token).get()
#     return ret
#
#
# def api_yt_get_me_accounts(user_token: str):
#     ret = FacebookApiCaller('me/accounts',
#                             bearer_token=user_token,).get()
#     return ret
#
#
# def api_yt_get_accounts_from_user(user_token: str, user_id: str):
#     ret = FacebookApiCaller(f'{user_id}/accounts',
#                             bearer_token=user_token,).get()
#     return ret
#
#
# def api_yt_get_page_token_from_user(user_token: str, page_id: str):
#     ret = FacebookApiCaller(page_id, bearer_token=user_token,
#                             params={"fields": "access_token"}).get()
#     return ret
#
#
# def api_yt_get_long_lived_token(token: str):
#     params = {
#         'grant_type': 'fb_exchange_token',
#         'client_id': settings.FACEBOOK_APP_CREDS['app_id'],
#         'client_secret': settings.FACEBOOK_APP_CREDS['app_secret'],
#         'fb_exchange_token': token,
#     }
#     ret = FacebookApiCaller(f'oauth/access_token',
#                             params=params).get()
#     return ret
