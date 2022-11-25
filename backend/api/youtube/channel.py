from backend.api.youtube._youtube_api_caller import YoutubeApiCaller

from django.conf import settings


def api_youtube_get_list_channel_by_token(access_token: str):

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


