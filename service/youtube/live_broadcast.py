from ._youtube_api_caller import YoutubeApiCaller

def get_active_live_with_access_token(access_token: str, max_results: int):
    params = {
        "maxResults": max_results,
        "part": "id,snippet,contentDetails,status",
        "broadcastStatus": "active",
    }
    ret = YoutubeApiCaller('liveBroadcasts', bearer_token = access_token, params=params).get()
    return ret