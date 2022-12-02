from ._youtube_api_caller import YoutubeApiCaller
from ._youtube_api_caller import YoutubeApiCaller

from django.conf import settings
import requests

def get_list_channel_by_token(access_token: str):

    params = {
        "part": "id,snippet",
        "mine": "true"
    }

    ret = YoutubeApiCaller(
        'channels', bearer_token=access_token, params=params).get()

    return ret


def api_youtube_get_list_channel_by_id(access_token: str, video_id: str):

    params = {
        "part": "id,snippet",
        "mine": "true"
    }

    ret = YoutubeApiCaller(
        'channels', bearer_token=access_token, params=params).get()

    return ret


def refresh_channel_token(refresh_token):

    response = requests.post(
        url="https://accounts.google.com/o/oauth2/token",
        data={
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID_FOR_LIVESHOWSELLER,  
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET_FOR_LIVESHOWSELLER,                                
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        })

    return response.status_code, response.json()

def get_live_broadcasts(access_token: str, max_results: int=100):
    params = {
        "maxResults": max_results,
        "part": "id,snippet,contentDetails,status",
        "broadcastStatus": "active",
    }
    ret = YoutubeApiCaller('liveBroadcasts', bearer_token = access_token, params=params).get()
    return ret

