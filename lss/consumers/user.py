import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer  

class LoginConsumer(WebsocketConsumer):
    def connect(self):

        self.user_subscription = "1"
        self.room_group_name = 'user_subscription_%s' % self.user_subscription
        
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

    # def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']
    #     print(message)

    # def chat_message(self, event):
    #     message = event['message']

    #     self.send(text_data=json.dumps({
    #         'message': message
    #     }))


    def notification_message(self, event):
        self.send(text_data=json.dumps(event))
