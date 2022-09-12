import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer  #async will hang untill finish
from api import models
import lib
import service
from automation import jobs


PLUGIN_SHOPIFY='shopify'
class ExportOrderConsumer(WebsocketConsumer):
    
    @lib.error_handle.error_handler.web_socket_error_handler.web_socket_error_handler
    def connect(self):

        campaign_id = self.scope['url_route']['kwargs']['campaign_id']

        api_user = lib.util.verify.Verify.get_seller_user_from_scope(self.scope)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)
        
        self.room_group_name = f'campaign_{campaign_id}_{PLUGIN_SHOPIFY}_order_export'

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

        campaign_id = self.scope['url_route']['kwargs']['campaign_id']

        api_user = lib.util.verify.Verify.get_seller_user_from_scope(self.scope)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        lib.util.verify.Verify.get_campaign_from_user_subscription(user_subscription,campaign_id)

        credential = user_subscription.user_plan.get('plugins',{}).get(PLUGIN_SHOPIFY)
        if not credential:
            raise lib.error_handle.error.api_error.ApiVerifyError('no_plugin')

        
        jobs.shopify.export_order_job(campaign_id,credential)
        # service.rq.queue.enqueue_general_queue(jobs.shopify.export_order_job, campaign_id = campaign_id, credential=credential)
        # print(campaign_id,api_user,user_subscription,credential)
        self.send(text_data=json.dumps({
            'type':'response_data',
            'data':{
                "message":'ok'
            } 
        }))

    def result_data(self, event):
        self.send(text_data=json.dumps(event))