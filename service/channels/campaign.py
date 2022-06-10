
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_comment_data(campaign_id, data):
    del data['_id']
    async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "comment_data","data":data})

def send_add_product_and_order_data(campaign_id, data):
    del data['_id']
    async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "add_product_and_order_data","data":data})
    
def send_update_product_and_order_data(campaign_id, data):
    del data['_id']
    async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "update_product_and_order_data","data":data})
    
def send_delete_product_and_order_data(campaign_id, data):
    del data['_id']
    async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "delete_product_and_order_data","data":data})

def send_order_data(campaign_id, data):
    del data['_id']
    async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "order_data","data":data})