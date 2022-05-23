from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    
    re_path(r'ws/campaign/(?P<campaign_id>\w+)/$', consumers.campaign.CampaignLiveConsumer.as_asgi()),
    re_path(r'ws/login/', consumers.user.LoginConsumer.as_asgi()),

]