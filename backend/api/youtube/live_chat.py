from backend.api.youtube._youtube_api_caller import YoutubeApiCaller
from django.conf import settings


def api_youtube_get_live_chat_comment(page_token: str, live_chat_id: str, max_results: int):
    params = {
        "key": settings.YOUTUBE_API_KEY,
        "maxResults": max_results,
        "part": "id,snippet,authorDetails",
        "liveChatId": live_chat_id,
        "pageToken": page_token
    }
    ret = YoutubeApiCaller('liveChat/messages', params=params).get()
    return ret


def api_youtube_post_live_chat_comment(api_key: str, access_token: str, live_chat_id: str, text: str):

    data = {
        "snippet": {
            "liveChatId": live_chat_id,
            "type": "textMessageEvent",
            "textMessageDetails": {
                "messageText": text
            }
        }
    }

    params = {
        "key": api_key,
        "part": "id,snippet",
    }

    ret = YoutubeApiCaller(
        'liveChat/messages', bearer_token=access_token, params=params, data=data).post()
    return ret
