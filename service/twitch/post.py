from ._twitch_api_caller import TwitchApiCaller
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
    data = { 'message': message }
    ret = TwitchApiCaller('helix/whispers', headers=headers, params=params, data=data).post()
    return ret