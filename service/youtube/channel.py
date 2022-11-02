from ._youtube_api_caller import YoutubeGoogleApiCaller

from django.conf import settings
import requests

def get_list_channel_by_token(access_token: str):

    params = {
        "part": "id,snippet",
        "mine": "true"
    }

    ret = YoutubeGoogleApiCaller(
        'channels', bearer_token=access_token, params=params).get()

    return ret


def api_youtube_get_list_channel_by_id(access_token: str, video_id: str):

    params = {
        "part": "id,snippet",
        "mine": "true"
    }

    ret = YoutubeGoogleApiCaller(
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
    # # code, refresh_token_response = api_google_post_refresh_token(refresh_token)


    # logs.append(["refresh status", code])
    # logs.append(["refresh data", refresh_token_response])
    # youtube_channel.update(token=refresh_token_response.get('access_token'),sync=False)

    # return refresh_token_response.get('access_token')

