import json

from django.conf import settings
from django.http import HttpResponse
from chat_bot.facebook.fb_func import *



def facebook_verify(request):
    mode = request.query_params.get('hub.mode', None)
    token = request.query_params.get('hub.verify_token', None)
    challenge = request.query_params.get('hub.challenge', None)

    if mode and token:
        if mode == 'subscribe' and token == settings.CHAT_BOT_FACEBOOK['VERIFY_TOKEN']:
            print('FACEBOOK_WEBHOOK_VERIFIED')
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse(status=403)


def facebook_receive(request):
    try:
        body = json.loads(request.body)
    except Exception:
        import traceback
        print(traceback.format_exc())
        return HttpResponse(status=400)
    print(body)
    if body.get('object') in ['page', 'instagram']:
        for entry in body.get('entry', []):
            try:
                webhook_event = entry['messaging'][0]
                page_id = entry['id']
                sender_psid = webhook_event['sender']['id']
                time_of_event = entry['time']

                if message := webhook_event.get('message'):
                    if message.get('text'):
                        handleTextMessage(body.get('object'), page_id, sender_psid, message)
                        print (message['text'], time_of_event)
                        
                    elif message.get('attachments'):
                        ...
                    elif message.get('quick_reply'):
                        ...
                elif postback := webhook_event.get('postback'):
                    print(postback, time_of_event)
            except Exception as e:
                import traceback
                print (traceback.format_exc())

        return HttpResponse('EVENT_RECEIVED', status=200)
    else:
        return HttpResponse(status=404)
