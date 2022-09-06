from django.urls import re_path
from . import consumers

from plugins.easy_store import consumers as easy_store_consumers
from plugins.ordr_startr import consumers as ordr_startr_consumers
websocket_urlpatterns = [
    
    re_path(r'ws/campaign/(?P<campaign_id>\w+)/$', consumers.campaign.CampaignLiveConsumer.as_asgi()),
    re_path(r'ws/login/', consumers.user.LoginConsumer.as_asgi()),

    #------------------------------------------plugins--------------------------------------------
    re_path(r'ws/plugin/easy_store/product/export', easy_store_consumers.export_product.ExportProductConsumer.as_asgi()),
    re_path(r'ws/plugin/easy_store/order/export/(?P<campaign_id>\w+)/$', easy_store_consumers.export_order.ExportOrderConsumer.as_asgi()),
    re_path(r'ws/plugin/ordr_startr/product/export', ordr_startr_consumers.export_product.ExportProductConsumer.as_asgi())

]