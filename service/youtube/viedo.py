from ._youtube_api_caller import YoutubeApiCaller
from django.conf import settings


def get_video_info_with_api_key(video_id: str):
    params = {
        "key": settings.YOUTUBE_API_KEY,
        "id": video_id,
        "part": "id,snippet,liveStreamingDetails",
    }
    ret = YoutubeApiCaller('videos', params=params).get()
    return ret

def get_video_info_with_access_token(access_token: str, video_id: str):
    params = {
        # "key": settings.YOUTUBE_API_KEY,
        "id": video_id,
        "part": "id,snippet,liveStreamingDetails",
    }
    ret = YoutubeApiCaller('videos', bearer_token=access_token, params=params).get()
    return ret

def get_video_comment_thread(page_token: str, video_id: str, max_results: int):
    params = {
        "key": settings.YOUTUBE_API_KEY,
        "videoId": video_id,
        "maxResults": max_results,
        "part": "id,snippet",
        "pageToken": page_token,
        "order": "time"
    }
    ret = YoutubeApiCaller('commentThreads', params=params).get()
    return ret


def post_video_comment(access_token: str, comment_thread_id: str, text: str):

    data = {
        "snippet": {
            "parentId": comment_thread_id,
            "textOriginal": text
        }
    }

    params = {
        "key": settings.YOUTUBE_API_KEY,
        "part": "id,snippet",
    }

    ret = YoutubeApiCaller(
        'comments', bearer_token=access_token, params=params, data=data).post()
    return ret
