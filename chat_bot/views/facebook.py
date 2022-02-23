from chat_bot.facebook.webhook import facebook_receive, facebook_verify
from rest_framework.decorators import api_view


@api_view(['GET', 'POST'])
def webhook_facebook(request):
    if request.method == 'GET':
        return facebook_verify(request)
    elif request.method == 'POST':
        return facebook_receive(request)
