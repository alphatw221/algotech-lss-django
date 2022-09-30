from ._fb_api_caller import FacebookApiCaller

def get_post(page_token: str, page_id:str, post_id: str):
    params = {
        "fields": "likes{id,name,pic_large},shares,sharedposts"
    }
    ret = FacebookApiCaller(f'{page_id}_{post_id}', bearer_token=page_token,
                            params=params).get()
    return ret

def get_post_likes(page_token: str, page_id:str, post_id: str, after: str = None, limit=100):
    params = {
        'limit': limit,
        'fields' :'id,name,pic_large' # id is PSID
    }
    if after:
        params['after'] = after
    ret = FacebookApiCaller(f'{page_id}_{post_id}/likes', bearer_token=page_token,
                            params=params).get()
    return ret


def get_post_comments(page_token: str, post_id: str, since: int = 1):
    params = {
        'since': since, 'order': 'chronological', 'limit': 100,
        'date_format': 'U', 'live_filter': 'no_filter',
        'fields': 'created_time,from{picture,name,id},message,id',
    }
    ret = FacebookApiCaller(f'{post_id}/comments', bearer_token=page_token,
                            params=params).get()
    return ret


def post_page_message_on_comment(page_token: str, comment_id: str, message_text: str):
    data = {
        "recipient": {"comment_id": comment_id},
        "message": {"text": message_text}
    }
    ret = FacebookApiCaller(f'me/messages', bearer_token=page_token,
                            data=data).post()
    return ret


def post_page_comment_on_comment(page_token: str, comment_id: str, message_text: str):
    data = {
        "message": message_text
    }
    ret = FacebookApiCaller(f'{comment_id}/comments', bearer_token=page_token,
                            data=data).post()
    return ret


def post_page_comment_on_post(page_token: str, post_id: str, message_text: str):
    data = {
        "message": message_text
    }
    ret = FacebookApiCaller(f'{post_id}/comments', bearer_token=page_token,
                            data=data).post()
    return ret


def post_page_action_on_comment(page_token: str, comment_id: str, message_text: str,
                                       to_message: bool = False, to_comment: bool = False):
    ret = {}
    if to_message:
        to_message_ret = post_page_comment_on_comment(
            page_token, comment_id, message_text)
        ret['to_message'] = to_message_ret
    if to_comment:
        to_comment_ret = post_page_comment_on_comment(
            page_token, comment_id, message_text)
        ret['to_comment'] = to_comment_ret
    return ret

def get_post_sharedpost(page_token: str, page_id:str, post_id: str, after: str = None, limit=100):
    params = {
        'limit': limit,
        'fields' :'id,from' # id is ASID
    }
    if after:
        params['after'] = after
    ret = FacebookApiCaller(f'{page_id}_{post_id}/sharedposts', bearer_token=page_token,
                            params=params).get()
    return ret

def post_get_live_video_object(page_token: str, page_id:str):
    params = {
        'status': 'LIVE_NOW'
    }
    ret = FacebookApiCaller(f'{page_id}/live_videos', bearer_token=page_token,
                            params=params).post()
    return ret
