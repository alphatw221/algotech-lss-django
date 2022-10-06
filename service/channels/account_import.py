
import traceback
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



def send_success_data(room_id, data):
    try:
        async_to_sync(get_channel_layer().group_send)(room_id, {"type": "success_data", "data": data})
    
    except Exception:
        print(traceback.format_exc())

def send_error_data(room_id, data):
    try:
        async_to_sync(get_channel_layer().group_send)(room_id, {"type": "error_data", "data": data})
    
    except Exception:
        print(traceback.format_exc())

def send_complete_data(room_id, data):
    try:
        async_to_sync(get_channel_layer().group_send)(room_id, {"type": "complete_data", "data": data})
    
    except Exception:
        print(traceback.format_exc())