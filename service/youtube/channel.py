from ._youtube_api_caller import YoutubeGoogleApiCaller

from django.conf import settings


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


