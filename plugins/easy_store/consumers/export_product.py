import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer  #async will hang untill finish
import lib
PLUGIN_EASY_STORE='easy_store'
class ExportProductConsumer(WebsocketConsumer):

    @lib.error_handle.error_handler.web_socket_error_handler.web_socket_error_handler
    def connect(self):

        api_user = lib.util.verify.Verify.get_seller_user_from_scope(self.scope)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        self.room_group_name = f'user_subscription_{user_subscription.id}_{PLUGIN_EASY_STORE}_product_export'


        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def result_data(self, event):
        self.send(text_data=json.dumps(event))