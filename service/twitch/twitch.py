from ._twitch_api_caller import TwitchApiCaller, TwitchOauthCaller
from django.conf import settings


def whisper_to_user(access_token: str, to_user_id: str, message: str):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': settings.TWITCH_CLIENT_ID
    }
    params = {
        'from_user_id': settings.TWITCH_FROM_USER_ID,
        'to_user_id': to_user_id
    }
    data = { 
        'message': message 
    }
    ret = TwitchApiCaller('helix/whispers', headers=headers, params=params, data=data).post()

    return ret

def get_token(code: str):
    headers = { 
        'Content-Type': 'application/x-www-form-urlencoded' 
    }
    data = {
        'client_id': settings.TWITCH_CLIENT_ID,
        'client_secret': settings.TWITCH_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.GCP_API_LOADBALANCER_URL,
    }
    ret = TwitchOauthCaller('oauth2/token', headers=headers, data=data).post()

    return ret

def get_user(access_token: str):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    ret = TwitchOauthCaller('oauth2/userinfo', headers=headers).get()

    return ret

def get_user_info(access_token: str, user_name: str):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': settings.TWITCH_CLIENT_ID
    }
    params = {
        'login': user_name
    }
    ret = TwitchApiCaller('helix/users', headers=headers, params=params).get()

    return ret

def api_twitch_validate_token(access_token: str):
    headers = {
        'Authorization': f'OAuth {access_token}',
    }
    ret = TwitchOauthCaller('oauth2/validate', headers=headers).get()

    return ret

def refresh_exchange_access_token(refresh_token: str):
    headers = { 
        'Content-Type': 'application/x-www-form-urlencoded' 
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.TWITCH_CLIENT_ID,
        'client_secret': settings.TWITCH_CLIENT_SECRET
    }
    ret = TwitchOauthCaller('oauth2/token', headers=headers, data=data).post()

    return ret
