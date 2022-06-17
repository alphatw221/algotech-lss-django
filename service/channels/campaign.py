
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_comment_data(campaign_id, data):
    del data['_id']
    async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "comment_data","data":data})
    
def send_order_data(campaign_id, data):
    async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "order_data","data":data})
    
def send_product_data(campaign_id, data):
    async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "product_data","data":data})
