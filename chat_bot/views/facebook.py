from chat_bot.facebook.webhook import facebook_receive, facebook_verify
from rest_framework.decorators import api_view
import requests
from django.conf import settings


@api_view(['GET', 'POST'])
def webhook_facebook(request):
    if request.method == 'GET':
        return facebook_verify(request)
    elif request.method == 'POST':
        if settings.GCP_API_LOADBALANCER_URL != "https://sb.liveshowseller.ph":
            r = requests.post('https://sb.liveshowseller.ph/chat_box/facebook/', params=request.POST)

        return facebook_receive(request)
