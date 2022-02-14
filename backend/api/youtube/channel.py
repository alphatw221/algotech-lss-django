from backend.api.youtube._youtube_api_caller import YoutubeGoogleApiCaller

from django.conf import settings


def api_youtube_get_list_channel(access_token: str):

    params = {
        "part": "id,snippet",
        "mine": "true"
    }

    #TODO GoogleApiCaller
    ret = YoutubeGoogleApiCaller(
        'channels', bearer_token=access_token, params=params).get()

    return ret
