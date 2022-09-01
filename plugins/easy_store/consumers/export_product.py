import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer  #async will hang untill finish
import lib
import service
from automation import jobs

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

    def receive(self, text_data):
        print(text_data)

        api_user = lib.util.verify.Verify.get_seller_user_from_scope(self.scope)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)

        credential = user_subscription.user_plan.get('plugins',{}).get(PLUGIN_EASY_STORE)
        if not credential:
            raise lib.error_handle.error.api_error.ApiVerifyError('no_plugin')
        print(credential)
        service.rq.queue.enqueue_general_queue(jobs.easy_store.export_product_job, user_subscription_id = user_subscription.id, credential=credential)
        self.send(text_data=json.dumps({
            'type':'response_data',
            'data':{
                "message":'ok'
            } 
        }))

    def result_data(self, event):
        self.send(text_data=json.dumps(event))