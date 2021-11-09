from config import logger, shopping_cart_init_url
from flask import jsonify, request

import traceback
from datetime import datetime, timedelta
# Import models from models directory
from api.utilities.api_orm_utilities import *
from api.utilities.api_utilities import *
from api.utilities.fb_campaign_summary import create_fb_campaign_summary
from api.utilities.fb_campaign_stat import update_fb_campaign_stat
from api.utilities.fb_campaign_order_capturing import capture_fb_campaign_comment

from config import connex_app


def _get_update_commnet_results(fb_campaigns_by_now):
    # TODO: threading here?
    update_commnet_results = []
    for fb_campaign in fb_campaigns_by_now:
        try:
            fb_campaign_comment_result = capture_fb_campaign_comment(
                fb_campaign)
            update_commnet_results.append(fb_campaign_comment_result)
        except:
            logger.error(traceback.format_exc())
    return update_commnet_results


def _get_update_stat_results(fb_campaigns_by_now):
    # TODO: threading here?
    update_stat_results = []
    for fb_campaign in fb_campaigns_by_now:
        try:
            fb_campaign_stat_result = update_fb_campaign_stat(
                fb_campaign.fb_campaign_id)
            update_stat_results.append(fb_campaign_stat_result)
        except:
            logger.error(traceback.format_exc())
    return update_stat_results


def _get_fb_campaign_summaries(fb_campaigns_by_end_time_delta):
    # TODO: threading here?
    fb_campaign_summaries = []
    print(fb_campaigns_by_end_time_delta)
    for fb_campaign in fb_campaigns_by_end_time_delta:
        try:
            fb_campaign_summary = create_fb_campaign_summary(
                fb_campaign.fb_campaign_id)
            fb_campaign_summaries.append(fb_campaign_summary)
        except:
            logger.error(traceback.format_exc())
    return fb_campaign_summaries


def _get_generated_orders(fb_campaigns_by_now):
    result = []
    for fb_campaign in fb_campaigns_by_now:
        fb_user_ids = orm_get_fb_campaign_order_fb_user_ids(
            fb_campaign.fb_campaign_id, 'valid')
        for fb_user_id in fb_user_ids:
            request = f'{shopping_cart_init_url}{fb_campaign.fb_campaign_id}/{fb_user_id.fb_user_id}/init'
            ret = requests_get(request)
        result.append({"fb_campaign_id": fb_campaign.fb_campaign_id,
                       "generated_orders": len(fb_user_ids)})
    return result
