
import traceback
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



def send_result_data(room_id, data):
    try:
        async_to_sync(get_channel_layer().group_send)(room_id, {"type": "result_data", "data": data})
    
    except Exception:
        print(traceback.format_exc())