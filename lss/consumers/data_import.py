import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer  
import lib
import uuid
class DataImportConsumer(WebsocketConsumer):

    @lib.error_handle.error_handler.web_socket_error_handler.web_socket_error_handler
    def connect(self):

        api_user = lib.util.verify.Verify.get_seller_user_from_scope(self.scope)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        room_group_name = str(uuid.uuid4())
        self.room_group_name = room_group_name
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({'type':'room_data','room_id':room_group_name}))

    def disconnect(self, close_code):

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def room_data(self, event):
        self.send(text_data=json.dumps(event))

    def result_data(self, event):
        self.send(text_data=json.dumps(event))
