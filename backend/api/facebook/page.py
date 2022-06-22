from backend.api.facebook._fb_api_caller import FacebookApiCaller


def api_fb_get_page_posts(page_token: str, page_id: str, limit: int):
    params = {
        'limit': limit
    }
    ret = FacebookApiCaller(f'{page_id}/posts', bearer_token=page_token,
                            params=params).get()
    return ret


def api_fb_post_page_message(page_token: str, page_id: str, recipient_id: str, message_text: str):
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    ret = FacebookApiCaller(f'{page_id}/messages', bearer_token=page_token,
                            data=data).post()
    return ret


def api_fb_get_page_picture(page_token: str, page_id: str, height: int, width: int):
    params = {
        'redirect': 0,
        'height': height,
        'width': width,
    }
    ret = FacebookApiCaller(f'v12.0/{page_id}/picture', bearer_token=page_token,
                            params=params).get()
    return ret


def api_fb_get_page_admin(page_token: str, page_id: str, user_id: str):
    ret = FacebookApiCaller(
        f'v2.2/{page_id}/roles', bearer_token=page_token).get()
    return ret


def api_fb_get_page_business_profile(page_token: str, page_id: str):
    params = {
        "fields": "instagram_business_account"
    }
    ret = FacebookApiCaller(f'v13.0/{page_id}', bearer_token=page_token,
                            params=params).get()
    return ret

def api_fb_get_comments_on_comment(page_token: str, comment_id: str):
    params = {
        'fields': 'created_time,from{picture,name,id},message,id',
    }
    ret = FacebookApiCaller(f'{comment_id}/comments', bearer_token=page_token,
                            params=params).get()
    return ret
