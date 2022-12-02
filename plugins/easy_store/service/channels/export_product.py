
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



PLUGIN_EASY_STORE = 'easy_store'

def send_result_data(user_subscription_id, data):
    async_to_sync(get_channel_layer().group_send)(f'user_subscription_{user_subscription_id}_{PLUGIN_EASY_STORE}_product_export', {"type": "result_data","data":data})
