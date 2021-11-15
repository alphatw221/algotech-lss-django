from django.conf import settings
from dataclasses import dataclass
from api.utils.api._api_caller import RestApiJsonCaller


@dataclass
class YoutubeApiCaller(RestApiJsonCaller):
    domain_url: str = settings.YOUTUBE_API_URL


def api_youtube_get_live_chat_comment(page_token: str, live_chat_id: str, max_results: int):
    params = {
        "key": settings.YOUTUBE_API_KEY,
        "masResults": max_results,
        "part": "id,snippet,authorDetails",
        "liveChatId": live_chat_id,
        "pageToken": page_token
    }
    ret = YoutubeApiCaller('liveChat/messages', params=params).get()
    return ret


def api_youtube_get_video_info(video_id: str):
    params = {
        "key": settings.YOUTUBE_API_KEY,
        "id": video_id,
        "part": "id,snippet,liveStreamingDetails",
    }
    ret = YoutubeApiCaller('videos', params=params).get()
    return ret


def api_youtube_get_video_comment(page_token: str, video_id: str, max_results: int):
    params = {
        "key": settings.YOUTUBE_API_KEY,
        "id": video_id,
        "masResults": max_results,
        "part": "id,snippet",
        "pageToken": page_token,
        "order": "time"
    }
    ret = YoutubeApiCaller('commentThreads', params=params).get()
    return ret
