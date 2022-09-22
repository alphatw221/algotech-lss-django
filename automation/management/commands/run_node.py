
from django.core.management.base import BaseCommand


from api import models
from automation import jobs

import service
import lib

from datetime import datetime
import config
import pottery

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
                self.leader_loop()




    @lib.util.timeloop.time_loop(30)
    def follower_loop(self):
        # print('i am follewer')
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
        print('run election')
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


    @lib.util.timeloop.time_loop(10)
    def leader_loop(self):
        # print('i am leader')
        if self.__new_leader_exist():
            self.position = POSITION_FOLLOWER
            return 'break'

        self.__heart_beating()

        rows=[]
        for campaign in models.campaign.campaign.Campaign.objects.filter(user_subscription__isnull=False, start_at__lt=datetime.utcnow(),end_at__gt=datetime.utcnow()):
            invalid_facebook = not campaign.facebook_campaign.get("post_id", None)
            invalid_instagram = not campaign.instagram_campaign.get("live_media_id", None)
            invalid_youtube = not campaign.youtube_campaign.get("live_video_id", None)
            invalid_twitch = not campaign.twitch_campaign.get("channel_name", None)
            invalid_tiktok = not campaign.tiktok_campaign.get("username", None)
            if invalid_facebook and invalid_instagram and invalid_youtube and invalid_twitch and invalid_tiktok:
                continue
            if not service.rq.job.exists(campaign.id):
                service.rq.queue.enqueue_unique_job_to_campaign_queue(jobs.campaign_job.campaign_job, campaign_id = campaign.id)
                rows.append([campaign.id, ""])
                continue

            job, job_status = service.rq.job.get_job_status(campaign.id)
            rows.append([campaign.id, job_status])
            if job_status == 'queued':
                count = service.redis.redis.get_count(campaign.id)
                if count >5:
                    job.delete()
                    service.redis.redis.delete(campaign.id)
                else:
                    service.redis.redis.increment(campaign.id)
            elif job_status in ('started', 'deferred'):
                # job.delete()
                continue
            elif job_status in ('finished', 'failed', 'canceled'):  #
                job.delete()
                service.redis.redis.delete(campaign.id)
                service.rq.queue.enqueue_unique_job_to_campaign_queue(jobs.campaign_job.campaign_job, campaign_id = campaign.id)

        lib.util.logger.print_table(["Campaign ID", "Status"],rows)

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