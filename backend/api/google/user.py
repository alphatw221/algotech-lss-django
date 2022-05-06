from django.conf import settings
from backend.api.google._google_api_caller import GoogleApiCaller, GoogleAccountApiCaller, GoogleOauth2ApiCaller


def api_google_get_me(token: str):
    code, ret = GoogleApiCaller('userinfo/v2/me', bearer_token=token).get()
    return code, ret


def api_google_get_userinfo(token: str):
    code, ret = GoogleApiCaller('oauth2/v2/userinfo', bearer_token=token).get()
    return code, ret


def api_google_get_token(code, redirect_uri):
    data = {
        "code": code,
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,
        # TODO keep it to settings
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,  # TODO keep it to settings
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    return GoogleAccountApiCaller("o/oauth2/token", data=data).get()


def api_google_post_refresh_token(refresh_token):
    data = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,
        # TODO keep it to settings
        "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,  # TODO keep it to settings
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    return GoogleOauth2ApiCaller("token", data=data).post()
