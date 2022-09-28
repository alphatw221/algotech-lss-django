from ._fb_api_caller import FacebookApiCaller



def send_private_message(page_token: str, comment_id: str, text: str):
    data = {
        "recipient": {"comment_id": comment_id},
        "message": {"text":text}
    }
    ret = FacebookApiCaller(f'me/messages', bearer_token=page_token,
                            data=data).post()
    return ret

def send_private_message_with_buttons(page_token: str, comment_id: str, text: str, buttons:list):
    # buttons = [
    #     {
    #         "type":"web_url",
    #         "url":"https://www.messenger.com",
    #         "title":"Visit Messenger"
    #     },
    #     {
    #         "type": "postback",
    #         "title": "<BUTTON_TEXT>",
    #         "payload": "<STRING_SENT_TO_WEBHOOK>"
    #     }
    # ]

    data = {
        "recipient": {"comment_id": comment_id},
        "message": {
            "attachment": {
            "type":"template",
            "payload":{
                "template_type":"button",
                "text":text,
                "buttons":buttons
            }
        }}
    }


   

    ret = FacebookApiCaller(f'me/messages', bearer_token=page_token,
                            data=data).post()
    return ret
