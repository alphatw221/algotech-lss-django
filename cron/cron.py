import arrow
from django_cron import CronJobBase, Schedule

from database.lss.campaign import Campaign
from backend.pymongo.mongodb import db
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from api.models.campaign.campaign import Campaign as M_Campaign


class TestCronJob(CronJobBase):
    RUN_EVERY_MINS = 60
    RUN_AT_TIMES = ['10:00', ]
    RETRY_AFTER_FAILURE_MINS = 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        run_at_times=RUN_AT_TIMES,
                        retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'TestCronJob'

    def do(self):
        ret = ''

        result = 'ok'
        ret += f'result: {result}\n'

        return ret
    
    
class CampaignReminderCronJob(CronJobBase):
    RUN_EVERY_MINS = 0.5
    # RUN_AT_TIMES = ['10:00', ]
    # RETRY_AFTER_FAILURE_MINS = 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        # run_at_times=RUN_AT_TIMES,
                        # retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS
                        )
    code = 'campaign_reminder'
    ALLOW_PARALLEL_RUNS = True

    def do(self):
        a = arrow.now()
        after_15min = arrow.utcnow().replace(second=0, microsecond=0).shift(minutes=+15)
        after_16min = after_15min.shift(minutes=+1)
        after_1hour = arrow.utcnow().replace(second=0, microsecond=0).shift(minutes=+60)
        after_61mins = after_1hour.shift(minutes=+1)
        campaings_start_after_15mins = list(db.api_campaign.aggregate([
            {
                "$match":{
                    "start_at":{
                        "$gte": after_15min.datetime,
                        "$lt": after_16min.datetime
                    }
                }
            },
            {
                "$project":{
                    "_id":0,
                    "user_subscription_id":1,
                    "title":1,
                    "remind_time": "15 mins"
                }
            }
        ]))
        campaings_start_after_1hour = list(db.api_campaign.aggregate([
            {
                "$match":{
                    "start_at":{
                        "$gte": after_1hour.datetime,
                        "$lt": after_61mins.datetime
                    }
                }
            },
            {
                "$project":{
                    "_id":0,
                    "user_subscription_id":1,
                    "title":1,
                    "remind_time": "an hour"
                }
            }
        ]))
        campaigns = campaings_start_after_15mins + campaings_start_after_1hour
        print(campaigns)
        channel_layer = get_channel_layer()
        b = arrow.now()
        # print(b-a)
        for campaign in campaigns:
            user_subscription_id = campaign['user_subscription_id']
            title = campaign['title']
            remind_time = campaign['remind_time']
            async_to_sync(channel_layer.group_send)(f"user_subscription_{user_subscription_id}", {"type": "notification_message","data":{"message":{"title": title, "remind_time": remind_time}}})