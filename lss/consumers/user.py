import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer  
import lib
import uuid
class LoginConsumer(WebsocketConsumer):

    @lib.error_handle.error_handler.web_socket_error_handler.web_socket_error_handler
    def connect(self):

        api_user = lib.util.verify.Verify.get_seller_user_from_scope(self.scope)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        
        self.room_group_name = 'user_subscription_%s' % user_subscription.id
        
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

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        #integrate with io platform

    def notification_message(self, event):
        self.send(text_data=json.dumps(event))

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

class AdminImportAccountConsumer(WebsocketConsumer):

    @lib.error_handle.error_handler.web_socket_error_handler.web_socket_error_handler
    def connect(self):
        auth_user = self.scope.get('user')
        if not auth_user.is_superuser:
            raise lib.error_handle.error.api_error.ApiVerifyError('not admin')

        room_group_name = str(uuid.uuid4())
        self.room_group_name = room_group_name
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({'type':'response_data','room_id':room_group_name}))

    def disconnect(self, close_code):

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    def result_data(self, event):
        self.send(text_data=json.dumps(event))