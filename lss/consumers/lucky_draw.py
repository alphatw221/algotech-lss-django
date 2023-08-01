import json
from asgiref.sync import async_to_sync
# from automation.jobs.crawler_job import crawler_shared_post_job
from channels.generic.websocket import WebsocketConsumer  
import lib
import uuid

import service
 
class SharedPostCrawlerConsumer(WebsocketConsumer):

    @lib.error_handle.error_handler.web_socket_error_handler.web_socket_error_handler
    def connect(self):
        print("lucky draw websocket connect")
        campaign_lucky_draw_id = self.scope['url_route']['kwargs']['campaign_lucky_draw_id']
        api_user = lib.util.verify.Verify.get_seller_user_from_scope(self.scope)
        user_subscription = lib.util.verify.Verify.get_user_subscription_from_api_user(api_user)
        self.room_group_name = 'campaign_lucky_draw_%s' % campaign_lucky_draw_id
        print(self.room_group_name)
        
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
        pass

        # text_data_json = json.loads(text_data)
        # action = text_data_json.get("action")
        # if action == "start_crawler":
        #     campaign_lucky_draw_id = text_data_json.get('lucky_draw_id')
        #     lucky_draw = lib.util.verify.Verify.get_lucky_draw(campaign_lucky_draw_id)
        #     username = lucky_draw.campaign.facebook_page.username
        #     post_id = lucky_draw.campaign.facebook_campaign.get("post_id", "")
        #     service.rq.queue.enqueue_general_queue(job=crawler_shared_post_job, room_id=self.room_group_name, lucky_draw_id=lucky_draw.id, facebook_page_username=username, post_id=post_id)
    def success_data(self, event):
        self.send(text_data=json.dumps(event))

    def error_data(self, event):
        self.send(text_data=json.dumps(event))

    def complete_data(self, event):
        self.send(text_data=json.dumps(event))