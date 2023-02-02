from django.conf import settings
from ..google._google_api_caller import GoogleApiCaller, GoogleAccountApiCaller, GoogleOauth2ApiCaller
import requests

def api_google_get_me(token: str):
    code, ret = GoogleApiCaller('userinfo/v2/me', bearer_token=token).get()
    return code, ret


def api_google_get_userinfo(token: str):
    code, ret = GoogleApiCaller('oauth2/v2/userinfo', bearer_token=token).get()
    return code, ret


def get_token_with_code(code, redirect_uri):
    data = {
        "code": code,
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,
        # TODO keep it to settings
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,  # TODO keep it to settings
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    return GoogleOauth2ApiCaller("token", data=data).post()


def api_google_post_refresh_token(refresh_token):
    data = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,
        # TODO keep it to settings
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,  # TODO keep it to settings
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    return GoogleOauth2ApiCaller("token", data=data).post()


def get_token(code, redirect_uri, client_id, client_secret):

    response = requests.post(
                    url="https://accounts.google.com/o/oauth2/token",
                    data={
                        "code": code,
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": redirect_uri,
                        # "redirect_uri": settings.WEB_SERVER_URL + "/bind_youtube_channels_callback",
                        "grant_type": "authorization_code"
                    }
                )
    return response.status_code, response.json()

