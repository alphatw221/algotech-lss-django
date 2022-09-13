from django.http import HttpResponse
from django.conf import settings
from rest_framework.decorators import api_view

from api import models
import lib
import service
import json



@api_view(['GET', 'POST'])
def facebook_messenger_webhook(request):
    try:
        if request.method == 'GET':
            mode = request.query_params.get('hub.mode', None)
            token = request.query_params.get('hub.verify_token', None)
            challenge = request.query_params.get('hub.challenge', None)

            if mode == 'subscribe' and token == settings.CHAT_BOT_FACEBOOK['VERIFY_TOKEN']:
                return HttpResponse(challenge, status=200)

            return HttpResponse(status=403)


        elif request.method == 'POST':
            body = json.loads(request.body)

            if body.get('object') not in ['page', 'instagram']:
                return HttpResponse(status=404)
            for entry in body.get('entry', []):
                webhook_event = entry.get('messaging',{})[0]
                page_id = entry.get('id', None)
                sender_psid = webhook_event.get('sender',{}).get('id')
                time_of_event = entry.get('time')


                if message := webhook_event.get('message'):
                    if message.get('is_echo'):
                        continue
                    if message.get('text'):
                        lib.helper.facebook_helper.handle_auto_response(body.get('object'), page_id, sender_psid, message)
                        print(type(message['text']))
                        # print(message['text'].encode('latin-1').decode())
                        print (message['text'], time_of_event)
                        
                    elif message.get('attachments'):
                        ...
                    elif message.get('quick_reply'):
                        ...
                elif postback := webhook_event.get('postback'):
                    print(postback, time_of_event)

            return HttpResponse('EVENT_RECEIVED', status=200)

                
    except Exception:
            import traceback
            print(traceback.format_exc())
            return HttpResponse(status=400)
