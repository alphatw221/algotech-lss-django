import os
import config
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS
    django.setup()
except Exception:
    pass

from automation import jobs
import lib
import service
import database

from datetime import datetime
import traceback


@lib.error_handle.error_handler.twitch_chat_job_error_handler.twitch_chat_job_error_handler
def twitch_chat_job(campaign_id, comments):

    campaign = database.lss.campaign.Campaign.get_object(id=int(campaign_id))
    user_subscription_data = database.lss.user_subscription.UserSubscription.get(id=campaign.data.get('user_subscription_id'))
    order_codes_mapping = jobs.campaign_job.OrderCodesMappingSingleton.get_mapping(campaign.id)
    twitch_channel = database.lss.twitch_channel.TwitchChannel.get_object(id=campaign.data.get('twitch_channel_id'))

    try:
        for uni_format_comment in comments:
            
            uni_format_comment['campaign_id'] = campaign_id,
            uni_format_comment['categories'] = service.nlp.classification.classify_comment_v2(uni_format_comment['message']),

            database.lss.campaign_comment.CampaignComment.create(**uni_format_comment, auto_inc=False)
            service.channels.campaign.send_comment_data(campaign.id, uni_format_comment)
            service.rq.queue.enqueue_comment_queue(jobs.comment_job.comment_job, campaign.data, user_subscription_data, 'twitch', twitch_channel.data, uni_format_comment, order_codes_mapping)
    except Exception as e:
        print(traceback.format_exc())