
from django.core.management.base import BaseCommand


from api import models
from automation import jobs

import service
import lib

from datetime import datetime
import config
import pottery

from multiprocessing import Process
import threading
import time
import uuid
POSITION_FOLLOWER = 'follower'
POSITION_LEADER = 'leader'

WAIT_HEART_BEAT_SECOND = 20
class Command(BaseCommand):

    position = POSITION_FOLLOWER
    node_name = ''

    def add_arguments(self, parser):
        pass
    
    def handle(self, *args, **options):

        self.node_name = str(uuid.uuid4())
        while True:
            if self.position == POSITION_FOLLOWER:
                self.follower_task()

            elif self.position == POSITION_LEADER:
                #i/o bound => threading
                leader_task = threading.Thread(target = self.leader_task) 
                level_1_thread = threading.Thread(target = self.capture_campaign_with_priority_level_1) 
                level_2_thread = threading.Thread(target = self.capture_campaign_with_priority_level_2)
                level_3_thread = threading.Thread(target = self.capture_campaign_with_priority_level_3)

                leader_task.start()
                level_1_thread.start()
                level_2_thread.start()
                level_3_thread.start()

                leader_task.join(timeout=70)
                level_1_thread.join(timeout=70)
                level_2_thread.join(timeout=70)
                level_3_thread.join(timeout=70)

                # level_1_process = Process(target=self.capture_campaign_with_priority_level_1)
                # level_2_process = Process(target=self.capture_campaign_with_priority_level_2)
                # level_3_process = Process(target=self.capture_campaign_with_priority_level_3)
                # level_1_process.start()
                # level_2_process.start()
                # level_3_process.start()
                # level_1_process.join()
                # level_2_process.join()
                # level_3_process.join()



    # @lib.util.timeloop.time_loop(30)
    @lib.util.timeloop.interval(times=1, interval=30)
    def follower_task(self):

        print('follower')
        
        info = self.__get_info()
        if not info :
            self.__run_election()
            return 'break'
        print(info)
        node_name, last_heart_beat = info.split(',')

        if datetime.utcnow().timestamp() - float(last_heart_beat) >= WAIT_HEART_BEAT_SECOND:
            self.__run_election()
            return  'break'

        # if node_name == config.COMMENT_CAPTURE_NODE_NAME:
        if node_name == self.node_name:
            self.position = POSITION_LEADER
            return 'break'



    def __run_election(self):

        lock = pottery.Redlock(key='leader', masters={service.redis.redis.redis_connection}, auto_release_time=5)
        with lock:
            info = self.__get_info()
            if not info:
                self.position = POSITION_LEADER
                self.__heart_beating()
                return
            node_name, last_heart_beat = info.split(',')
            if datetime.utcnow().timestamp() - float(last_heart_beat) >= WAIT_HEART_BEAT_SECOND:
                self.position = POSITION_LEADER
                self.__heart_beating()
                return

    @lib.util.timeloop.interval(times=12, interval=5)
    def leader_task(self):

        if self.__new_leader_exist():
            self.position = POSITION_FOLLOWER
            return 'break'

        self.__heart_beating()

    @lib.util.timeloop.interval(times=12, interval=5)
    def capture_campaign_with_priority_level_1(self):
        
        if self.position == POSITION_FOLLOWER:
            return 'break'
        # if self.__new_leader_exist():
        #     self.position = POSITION_FOLLOWER
        #     return 'break'

        # self.__heart_beating()

        rows=[]
        for campaign in models.campaign.campaign.Campaign.objects.filter(user_subscription__isnull=False, start_at__lt=datetime.utcnow(),end_at__gt=datetime.utcnow(), priority=1):
            self.__capture_campaign(campaign, rows)
        lib.util.logger.print_table(["Level 1 Campaign ID", "Status"],rows)

    # @lib.util.timeloop.time_loop(20)
    @lib.util.timeloop.interval(times=3, interval=20)
    def capture_campaign_with_priority_level_2(self):

        if self.position == POSITION_FOLLOWER:
            return 'break'
        
        # if self.__new_leader_exist():
        #     self.position = POSITION_FOLLOWER
        #     return 'break'

        # self.__heart_beating()

        rows=[]
        for campaign in models.campaign.campaign.Campaign.objects.filter(user_subscription__isnull=False, start_at__lt=datetime.utcnow(),end_at__gt=datetime.utcnow(), priority=2):
            self.__capture_campaign(campaign, rows)
        lib.util.logger.print_table(["Level 2 Campaign ID", "Status"],rows)

    # @lib.util.timeloop.time_loop(60)
    @lib.util.timeloop.interval(times=1, interval=60)
    def capture_campaign_with_priority_level_3(self):

        if self.position == POSITION_FOLLOWER:
            return 'break'
        
        # if self.__new_leader_exist():
        #     self.position = POSITION_FOLLOWER
        #     return 'break'

        # self.__heart_beating()

        lib.util.google_cloud_monitoring.CampaignQueueLengthMetric.write_time_series(len(service.rq.queue.campaign_queue.jobs))
        lib.util.google_cloud_monitoring.CommentQueueLengthMetric.write_time_series(len(service.rq.queue.comment_queue.jobs))


        rows=[]
        for campaign in models.campaign.campaign.Campaign.objects.filter(user_subscription__isnull=False, start_at__lt=datetime.utcnow(),end_at__gt=datetime.utcnow(), priority__gte=3):
            self.__capture_campaign(campaign, rows)
        lib.util.logger.print_table(["Level 3 Campaign ID", "Status"],rows)

    def __capture_campaign(self, campaign, rows):


        invalid_facebook = not campaign.facebook_campaign.get("post_id", None)
        invalid_sub_facebook = not campaign.sub_facebook_campaign.get("post_id", None)
        invalid_sub_facebook_3 = not campaign.sub_facebook_campaign_3.get("post_id", None)
        invalid_sub_facebook_4 = not campaign.sub_facebook_campaign_4.get("post_id", None)
        invalid_sub_facebook_5 = not campaign.sub_facebook_campaign_5.get("post_id", None)
        invalid_sub_facebook_6 = not campaign.sub_facebook_campaign_6.get("post_id", None)
        invalid_instagram = not campaign.instagram_campaign.get("live_media_id", None)
        invalid_youtube = not campaign.youtube_campaign.get("live_video_id", None)


        # invalid_twitch = not campaign.twitch_campaign.get("channel_name", None)
        # invalid_tiktok = not campaign.tiktok_campaign.get("username", None)
        if invalid_facebook and invalid_sub_facebook and invalid_sub_facebook_3 and invalid_sub_facebook_4 and invalid_sub_facebook_5 and invalid_sub_facebook_6 and invalid_instagram and invalid_youtube :
            
            rows.append([campaign.id, "invalid"])
            return
        if not service.rq.job.exists(campaign.id):
            service.rq.queue.enqueue_campaign_queue(jobs.campaign_job.campaign_job, campaign_id = campaign.id)
            rows.append([campaign.id, ""])
            return

        job, job_status = service.rq.job.get_job_status(campaign.id)
        rows.append([campaign.id, job_status])
        service.rq.queue.enqueue_campaign_queue(jobs.campaign_job.campaign_job, campaign_id = campaign.id)


    def __new_leader_exist(self):

        info = self.__get_info()
        if not info :
            return False

        node_name, last_heart_beat = info.split(',')

        if datetime.utcnow().timestamp() - float(last_heart_beat) >= WAIT_HEART_BEAT_SECOND:
            return False

        # if node_name == config.COMMENT_CAPTURE_NODE_NAME:
        if node_name == self.node_name:
            return False
        
        return True

    def __get_info(self):
        _byte = service.redis.redis.get('leader')
        if _byte == None:
            return ''
        else:
            return _byte.decode()

    def __heart_beating(self):
        if self.position != POSITION_LEADER:
            return
        # service.redis.redis.set('leader',f'{config.COMMENT_CAPTURE_NODE_NAME}-{datetime.utcnow().timestamp()}')
        service.redis.redis.set('leader',f'{self.node_name},{datetime.utcnow().timestamp()}')