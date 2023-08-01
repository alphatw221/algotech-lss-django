from django.urls import re_path
from . import consumers



websocket_urlpatterns = [
    
    re_path(r'ws/campaign/(?P<campaign_id>\w+)/$', consumers.campaign.CampaignLiveConsumer.as_asgi()),
    re_path(r'ws/login/', consumers.user.LoginConsumer.as_asgi()),
    re_path(r'ws/admin/account/import/', consumers.user.AdminImportAccountConsumer.as_asgi()),
    re_path(r'ws/data/import/', consumers.data_import.DataImportConsumer.as_asgi()),
    re_path(r'ws/lucky_draw/share_post/crawler/(?P<campaign_lucky_draw_id>\w+)/$', consumers.lucky_draw.SharedPostCrawlerConsumer.as_asgi()),
    
]