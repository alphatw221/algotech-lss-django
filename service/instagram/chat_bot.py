from backend.api.facebook._fb_api_caller import FacebookApiCaller, FacebookApiV12Caller

def api_ig_post_page_message_chat_bot(relate_fb_page_id:str, page_token: str, recipient_id: str, message: dict):
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message
        }
    }
    ret = FacebookApiCaller(f'{relate_fb_page_id}/messages', bearer_token=page_token,
                            data=data).post()
    return ret