from backend.api.facebook._fb_api_caller import FacebookApiCaller


def api_fb_get_post_likes(page_token: str, post_id: str, since: int = 1):
    params = {
        'limit': 100
    }
    ret = FacebookApiCaller(f'{post_id}/likes', bearer_token=page_token,
                            params=params).get()
    return ret


def api_fb_get_post_comments(page_token: str, post_id: str, since: int = 1):
    params = {
        'since': since, 'order': 'chronological', 'limit': 100,
        'date_format': 'U', 'live_filter': 'no_filter',
        'fields': 'created_time,from{picture,name,id},message,id',
    }
    ret = FacebookApiCaller(f'{post_id}/comments', bearer_token=page_token,
                            params=params).get()
    return ret


def api_fb_post_page_message_on_comment(page_token: str, comment_id: str, message_text: str):
    data = {
        "recipient": {"comment_id": comment_id},
        "message": {"text": message_text}
    }
    ret = FacebookApiCaller(f'me/messages', bearer_token=page_token,
                            data=data).post()
    return ret


def api_fb_post_page_comment_on_comment(page_token: str, comment_id: str, message_text: str):
    data = {
        "message": message_text
    }
    ret = FacebookApiCaller(f'{comment_id}/comments', bearer_token=page_token,
                            data=data).post()
    return ret


def api_fb_post_page_comment_on_post(page_token: str, post_id: str, message_text: str):
    data = {
        "message": message_text
    }
    ret = FacebookApiCaller(f'{post_id}/comments', bearer_token=page_token,
                            data=data).post()
    return ret


def api_fb_post_page_action_on_comment(page_token: str, comment_id: str, message_text: str,
                                       to_message: bool = False, to_comment: bool = False):
    ret = {}
    if to_message:
        to_message_ret = api_fb_post_page_message_on_comment(
            page_token, comment_id, message_text)
        ret['to_message'] = to_message_ret
    if to_comment:
        to_comment_ret = api_fb_post_page_comment_on_comment(
            page_token, comment_id, message_text)
        ret['to_comment'] = to_comment_ret
    return ret
