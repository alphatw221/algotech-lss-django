from ..facebook._fb_api_caller import FacebookApiCaller, FacebookApiV12Caller


def post_id_list(token: str, bussiness_id: str):
    ret = FacebookApiCaller(f'{bussiness_id}/media', bearer_token=token).get()
    return ret


def get_post_likes(token: str, post_id: str, after: str = None):
    params = {
        'limit': 100
    }
    if after:
        params['after'] = after
    ret = FacebookApiCaller(f'{post_id}/likes', bearer_token=token,
                            params=params).get()
    return ret


def get_post_comments(page_token: str, post_id: str, after_page):
    params = {
        'limit': 25,
        'pretty': 0,
        'fields': 'from,text,timestamp'
    }
    if after_page:
        params['after'] = after_page
        
    return FacebookApiV12Caller(f'{post_id}/comments', bearer_token=page_token, params=params).get()

def get_post_media_url(page_token: str, media_id: str):
    params = {
        'fields': 'media_url'
    }
    return FacebookApiV12Caller(f'{media_id}/', bearer_token=page_token, params=params).get()
        
    return FacebookApiV12Caller(f'{post_id}/comments', bearer_token=page_token, params=params).get()
def post_page_message_on_comment(page_token: str, comment_id: str, message: dict):
    data = {
        "message": message
    }
    ret = FacebookApiCaller(f'{comment_id}/replies', bearer_token=page_token,
                            data=data).post()
    return ret


def private_message(page_token: str, recipient_id: str, message: str):
    data = {
        "recipient": {"comment_id": recipient_id},
        "message": {"text": message}
    }

    return FacebookApiV12Caller(f'me/messages?access_token={page_token}', data=data).post()