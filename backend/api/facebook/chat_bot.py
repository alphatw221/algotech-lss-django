from backend.api.facebook._fb_api_caller import FacebookApiCaller


def api_fb_post_page_message_chat_bot(page_token: str, recipient_id: str, message: dict):
    data = {
        "recipient": {"id": recipient_id},
        "message": message
    }
    ret = FacebookApiCaller(f'me/messages', bearer_token=page_token,
                            data=data).post()
    return ret
