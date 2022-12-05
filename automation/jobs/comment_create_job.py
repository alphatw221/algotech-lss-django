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


@lib.error_handle.error_handler.comment_job_error_handler.comment_job_error_handler
def comment_create_job(campaign_id, comments, platform, push_comment:bool):

    campaign = database.lss.campaign.Campaign.get_object(id=int(campaign_id))
    user_subscription_data = database.lss.user_subscription.UserSubscription.get(id=campaign.data.get('user_subscription_id'))
    order_codes_mapping = jobs.campaign_job.OrderCodesMappingSingleton.get_mapping(campaign.id)

    if platform == 'twitch':
        platform_instance_data = database.lss.twitch_channel.TwitchChannel.get(id=campaign.data.get('twitch_channel_id'))
    elif platform == 'tiktok':
        platform_instance_data = {}

    texts = [comment.get('message') for comment in comments]
    comments_category = service.nlp.classification.classify_comment_v2(texts=texts)

    if len(comments) != len(comments_category):
        comments_category = [ [] for _ in range(len(comments)) ]

    for i, comment in enumerate(comments):

        comment['categories'] = comments_category[i]
        comment['created_time'] = int(datetime.now().timestamp())
        comment['campaign_id'] = campaign_id
        try:
            database.lss.campaign_comment.CampaignComment.create(**comment, auto_inc=False)
        except Exception as e: #duplicate key error might happen here

            continue

        if push_comment:
            service.channels.campaign.send_comment_data(campaign.id, comment)

        service.rq.queue.enqueue_comment_queue(jobs.comment_job_v2.comment_job, campaign.data, user_subscription_data, platform, platform_instance_data, comment, order_codes_mapping)
    
    