import json

from django.conf import settings
from django.http import HttpResponse
from rest_framework import status


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
    except:
        return HttpResponse(status=400)
    print(body)

    if body.get('object') == 'page':
        for entry in body.get('entry', []):
            webhook_event = entry['messaging'][0]
            page_id = entry['id']
            time_of_event = entry['time']
            sender_psid = webhook_event['sender.id']

            try:
                if message := webhook_event.get('message'):
                    if message.get('text'):
                        print(message, time_of_event)
                        # handleTextMessage(page_id, sender_psid, message)
                    elif message.get('attachments'):
                        ...
                    elif message.get('quick_reply'):
                        ...
                elif postback := webhook_event.get('postback'):
                    ...
            except:
                ...

        return HttpResponse('EVENT_RECEIVED', status=200)
    else:
        return HttpResponse(status=404)


"""
// Iterate over each entry - there may be multiple if batched
body.entry.forEach(function (entry) {
    // Gets the body of the webhook event
    let webhook_event = entry.messaging[0]

    // console.log(webhook_event) // FIXME DEBUG

    // Get the event status
    let page_id = entry.id
    let time_of_event = entry.time
    let sender_psid = webhook_event.sender.id

    try {
    if (webhook_event.message) {
        let message = webhook_event.message

        if (message.quick_reply) {
        // handleQuickReply(page_id, sender_psid, message.quick_reply)
        } else if (message.attachments) {
        // handleAttachmentMessage(page_id, sender_psid, message)
        } else if (message.text) {
        handleTextMessage(page_id, sender_psid, message)
        }
    } else if (webhook_event.postback) {
        // handlePostback(page_id, sender_psid, webhook_event.postback)
    }
    } catch (error) {
    console.error(error)
    }
})

// Return a '200 OK' response to all events
res.status(200).send('EVENT_RECEIVED')
"""
