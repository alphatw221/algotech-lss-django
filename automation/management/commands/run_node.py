
from django.core.management.base import BaseCommand


from api import models
from automation import jobs

import service
import lib

from datetime import datetime
import config
import pottery

from multiprocessing import Process

POSITION_FOLLOWER = 'follower'
POSITION_LEADER = 'leader'

WAIT_HEART_BEAT_SECOND = 20
class Command(BaseCommand):

    position = POSITION_FOLLOWER

    def add_arguments(self, parser):
        pass
    
    def handle(self, *args, **options):
        while True:
            if self.position == POSITION_FOLLOWER:
                self.follower_loop()
            elif self.position == POSITION_LEADER:
                level_1_process = Process(target=self.capture_campaign_with_priority_level_1)
                level_2_process = Process(target=self.capture_campaign_with_priority_level_2)
                level_3_process = Process(target=self.capture_campaign_with_priority_level_3)
                level_1_process.start()
                level_2_process.start()
                level_3_process.start()
                level_1_process.join()
                level_2_process.join()
                level_3_process.join()



    @lib.util.timeloop.time_loop(30)
    def follower_loop(self):

        info = service.redis.redis.get('leader').decode()
        if not info :
            self.__run_election()
            return 'break'
        node_name, last_heart_beat = info.split('-')

        if datetime.utcnow().timestamp() - float(last_heart_beat) >= WAIT_HEART_BEAT_SECOND:
            self.__run_election()
            return 'break'

        if node_name == config.COMMENT_CAPTURE_NODE_NAME:
            self.position = POSITION_LEADER
            return 'break'
    

    def __run_election(self):

        lock = pottery.Redlock(key='leader', masters={service.redis.redis.redis_connection}, auto_release_time=5)
        with lock:
            info = service.redis.redis.get('leader').decode()
            if not info:
                self.position = POSITION_LEADER
                self.__heart_beating()
                return
            node_name, last_heart_beat = info.split('-')
            if datetime.utcnow().timestamp() - float(last_heart_beat) >= WAIT_HEART_BEAT_SECOND:
                self.position = POSITION_LEADER
                self.__heart_beating()
                return

    @lib.util.timeloop.time_loop(5)
    def capture_campaign_with_priority_level_1(self):

        if self.__new_leader_exist():
            self.position = POSITION_FOLLOWER
            return 'break'

        self.__heart_beating()

        rows=[]
        for campaign in models.campaign.campaign.Campaign.objects.filter(user_subscription__isnull=False, start_at__lt=datetime.utcnow(),end_at__gt=datetime.utcnow(), priority=1):
            self.__capture_campaign(campaign, rows)
        lib.util.logger.print_table(["Level 1 Campaign ID", "Status"],rows)

    @lib.util.timeloop.time_loop(20)
    def capture_campaign_with_priority_level_2(self):

        if self.__new_leader_exist():
            self.position = POSITION_FOLLOWER
            return 'break'

        self.__heart_beating()

        rows=[]
        for campaign in models.campaign.campaign.Campaign.objects.filter(user_subscription__isnull=False, start_at__lt=datetime.utcnow(),end_at__gt=datetime.utcnow(), priority=2):
            self.__capture_campaign(campaign, rows)
        lib.util.logger.print_table(["Level 2 Campaign ID", "Status"],rows)

    @lib.util.timeloop.time_loop(60)
    def capture_campaign_with_priority_level_3(self):

        if self.__new_leader_exist():
            self.position = POSITION_FOLLOWER
            return 'break'

        self.__heart_beating()

        rows=[]
        for campaign in models.campaign.campaign.Campaign.objects.filter(user_subscription__isnull=False, start_at__lt=datetime.utcnow(),end_at__gt=datetime.utcnow(), priority=3):
            self.__capture_campaign(campaign, rows)
        lib.util.logger.print_table(["Level 3 Campaign ID", "Status"],rows)

    def __capture_campaign(self, campaign, rows):

        invalid_facebook = not campaign.facebook_campaign.get("post_id", None)
        invalid_instagram = not campaign.instagram_campaign.get("live_media_id", None)
        invalid_youtube = not campaign.youtube_campaign.get("live_video_id", None)
        invalid_twitch = not campaign.twitch_campaign.get("channel_name", None)
        invalid_tiktok = not campaign.tiktok_campaign.get("username", None)
        if invalid_facebook and invalid_instagram and invalid_youtube and invalid_twitch and invalid_tiktok:
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

        info = service.redis.redis.get('leader').decode()
        if not info :
            return False

        node_name, last_heart_beat = info.split('-')

        if datetime.utcnow().timestamp() - float(last_heart_beat) >= WAIT_HEART_BEAT_SECOND:
            return False

        if node_name == config.COMMENT_CAPTURE_NODE_NAME:
            return False
        
        return True



    def __heart_beating(self):
        if self.position != POSITION_LEADER:
            return
        service.redis.redis.set('leader',f'{config.COMMENT_CAPTURE_NODE_NAME}-{datetime.utcnow().timestamp()}')