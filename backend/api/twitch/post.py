from backend.api.twitch._twitch_api_caller import TwitchOAUTHApiCaller
from django.conf import settings

def api_twitch_get_access_token():
    headers = {
        'Client-Id': settings.TWITCH_CLIENT_ID,
        'Content-Type': 'application/json'
    }

    params = {
        'client_id': settings.TWITCH_CLIENT_ID,
        'client_secret': settings.TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': 'channel%3Amanage%3Apolls+channel%3Aread%3Apolls'
    }
    
    ret = TwitchOAUTHApiCaller(f'token', params=params, headers=headers).post()
    return ret