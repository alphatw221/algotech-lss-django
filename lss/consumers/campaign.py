import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer  #async will hang untill finish
import lib
class CampaignLiveConsumer(WebsocketConsumer):

    @lib.error_handle.error_handler.web_socket_error_handler.web_socket_error_handler
    def connect(self):

        campaign_id = self.scope['url_route']['kwargs']['campaign_id']
        # campaign_id = 440

        api_user = lib.util.verify.Verify.get_seller_user_from_scope(self.scope)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)
        
        self.room_group_name = 'campaign_%s' % campaign_id

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
    #     message = text_data_json.get('message')
    #     #integrate with io platform

    def cart_data(self, event):
        self.send(text_data=json.dumps(event))

    def comment_data(self, event):
        self.send(text_data=json.dumps(event))

    def comments_data(self, event):
        self.send(text_data=json.dumps(event))

    def order_data(self, event):
        self.send(text_data=json.dumps(event))

    def product_data(self, event):
        self.send(text_data=json.dumps(event))