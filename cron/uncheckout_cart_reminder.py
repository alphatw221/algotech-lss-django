import os
import sys

import arrow
import django
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django_cron import CronJobBase, Schedule
from automation.jobs.send_reminder_messages import send_reminder_messages_job
import database

import service
from api import models
import plugins as lss_plugins
from django.conf import settings

class UncheckoutCartReminderCronJob(CronJobBase):
    RUN_EVERY_MINS = 0.5
    # RUN_AT_TIMES = ['10:00', ]
    # RETRY_AFTER_FAILURE_MINS = 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        # run_at_times=RUN_AT_TIMES,
                        # retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS
                        )
    code = 'uncheckout_cart_reminder'
    ALLOW_PARALLEL_RUNS = True

    def do(self):
        start_time = arrow.now()
        utc_time_four_hours_ago = arrow.utcnow().shift(hours=-4)
        campaigns_ended_over_4_hours = models.campaign.campaign.Campaign.objects.filter(end_at__gte=utc_time_four_hours_ago.datetime) #, end_at__lt=utc_time_four_hours_ago.shift(minutes=+1).datetime)
        carts = [cart for campaign in campaigns_ended_over_4_hours for cart in campaign.carts.all() if len(cart.products) > 0]
        for cart in carts:
            pymongo_cart = database.lss.cart.Cart.get(id=cart.id)
            service.rq.queue.enqueue_general_queue(job=send_reminder_messages_job, pymongo_cart=pymongo_cart, user_subscription_id=cart.campaign.user_subscription.id)
        end_time = arrow.now()
        print(end_time-start_time)