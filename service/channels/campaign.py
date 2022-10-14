
import traceback
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_comment_data(campaign_id, data):

    try:
        async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "comment_data","data":data})    
    except Exception:
        print(traceback.format_exc())

def send_order_data(campaign_id, data):
    try:
        del data['_id']
        del data['created_at']
        del data['updated_at']
        del data['lock_at']

        # print(data)
        async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "order_data","data":data})
    except Exception:
        print(traceback.format_exc())

def send_cart_data(campaign_id, data):
    # try:
    del data['_id']
    del data['created_at']
    del data['updated_at']
    del data['lock_at']

    # print(data)
    async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "cart_data","data":data})
    # except Exception:
    #     print(traceback.format_exc())
    
def send_product_data(campaign_id, data):
    # try:
    async_to_sync(get_channel_layer().group_send)(f"campaign_{campaign_id}", {"type": "product_data","data":data})
    
    # except Exception:
    #     print(traceback.format_exc())