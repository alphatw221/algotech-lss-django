from ._fb_api_caller import FacebookApiCaller

def get_user_picture(user_asid:str, page_token: str):
    params = {
        'fields': "id,name,picture"
    }
    ret = FacebookApiCaller(user_asid, bearer_token=page_token, params=params).get()
    return ret

def get_page_posts(page_token: str, page_id: str, limit: int):
    params = {
        'limit': limit,
        'fields': 'attachments{media},message,created_time'
    }
    ret = FacebookApiCaller(f'{page_id}/posts', bearer_token=page_token,
                            params=params).get()
    return ret


def post_page_message(page_token: str, page_id: str, recipient_id: str, message_text: str):
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    ret = FacebookApiCaller(f'{page_id}/messages', bearer_token=page_token,
                            data=data).post()
    return ret


def get_page_picture(page_token: str, page_id: str, height: int, width: int):
    params = {
        'redirect': 0,
        'height': height,
        'width': width,
    }
    ret = FacebookApiCaller(f'v12.0/{page_id}/picture', bearer_token=page_token,
                            params=params).get()
    return ret


def get_page_admin(page_token: str, page_id: str, user_id: str):
    ret = FacebookApiCaller(
        f'v2.2/{page_id}/roles', bearer_token=page_token).get()
    return ret


def get_page_business_profile(page_token: str, page_id: str):
    params = {
        "fields": "instagram_business_account"
    }
    ret = FacebookApiCaller(f'v13.0/{page_id}', bearer_token=page_token,
                            params=params).get()
    return ret

def get_comments_on_comment(page_token: str, comment_id: str):
    params = {
        'fields': 'created_time,from{picture,name,id},message,id',
    }
    ret = FacebookApiCaller(f'{comment_id}/comments', bearer_token=page_token,
                            params=params).get()
    return ret

def post_setup_webhook(page_token: str, page_id: str, subscribed_fields="messages, messaging_postbacks"):
    params = {
        'subscribed_fields': subscribed_fields,
    }
    ret = FacebookApiCaller(f'{page_id}/subscribed_apps', bearer_token=page_token,
                            params=params).post()
    return ret

def subscribe_webhook(page_token: str, page_id: str, subscribed_fields=["messages", "messaging_postbacks"]):
    params = {
        'subscribed_fields': ','.join(subscribed_fields),
    }
    ret = FacebookApiCaller(f'{page_id}/subscribed_apps', bearer_token=page_token,
                            params=params).post()
    return ret

def delete_page_webhook(page_token: str, page_id: str):
    ret = FacebookApiCaller(f'{page_id}/subscribed_apps', bearer_token=page_token).delete()
    return ret

def post_send_quick_replies(page_token:str, recipient_id: str, replies_options: list):
    """_summary_

    Args:
        recipient_id (str): IGSID
        replies_options (list): 
        ex. 
            [
                {
                    "content_type":"text",
                    "title":"<TITLE_1>",
                    "payload":"<POSTBACK_PAYLOAD_1>"
                },
                {
                    "content_type":"text",
                    "title":"<TITLE_2>",
                    "payload":"<POSTBACK_PAYLOAD_2>"
                }
            ]
    """
    params = {
        "recipient":{
            "id": recipient_id
        },
        "messaging_type": "RESPONSE",
        "message":{
            "text": "",
            "quick_replies": replies_options
        }
    }
    ret = FacebookApiCaller("me/messages", bearer_token=page_token, params=params).post()
    return ret

def get_page_videos(page_token: str, page_id: str, limit: int):
    params = {
        'limit': limit,
        'fields': 'created_time,embeddable,embed_html,title,description,live_status,from'
    }
    ret = FacebookApiCaller(f'{page_id}/videos', bearer_token=page_token,
                            params=params).get()
    return ret

def get_live_video(page_token: str, page_id:str, broadcast_status:list=["LIVE"], limit:int=100):
    params = {
        'limit': limit,
        'broadcast_status': f"{broadcast_status}",
        'fields': 'title,status,embed_html,video,broadcast_start_time,description,from'
    }
    ret = FacebookApiCaller(f'{page_id}/live_videos', bearer_token=page_token,
                            params=params).get()
    return ret

def post_get_live_video_object(page_token: str, page_id:str):
    params = {
        'status': 'LIVE_NOW'
    }
    ret = FacebookApiCaller(f'{page_id}/live_videos', bearer_token=page_token,
                            params=params).post()
    return ret
        
    