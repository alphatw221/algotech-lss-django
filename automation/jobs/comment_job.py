import os
import django
from django.conf import settings
try:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'lss.settings'  # for rq_job
    django.setup()
except Exception:
    pass
from api.utils.common.order_helper import PreOrderHelper, PreOrderErrors

from backend.utils.text_processing.command_processor import \
    CommandTextProcessor
from backend.utils.text_processing.order_code_processor import \
    OrderCodeTextProcessor
from backend.i18n.comment_command import i18n_get_comment_command_response
from backend.i18n.cart_product_request import (i18n_get_additional_text,
                                               i18n_get_request_response)
from backend.api.facebook.post import (api_fb_post_page_comment_on_comment,
                                       api_fb_post_page_message_on_comment)
from backend.api.youtube.live_chat import api_youtube_post_live_chat_comment

from api.models.order.pre_order import api_pre_order_template
from backend.pymongo.mongodb import db, client, get_incremented_filed
from bson.objectid import ObjectId
from api.utils.common.verify import ApiVerifyError
from datetime import datetime
from api.utils.error_handle.error_handler.comment_job_error_handler import comment_job_error_handler


@comment_job_error_handler
def comment_job(campaign, platform_name, platform, comment, order_codes_mapping):
    # try:
    command = CommandTextProcessor.process(comment['message'])
    if command:
        command_responding(platform_name, platform,
                           campaign, comment, command)
        return

    # print(order_codes_mapping)
    order_placement = None
    for order_code, campaign_product in order_codes_mapping.items():
        qty = OrderCodeTextProcessor.process(
            comment['message'], order_code)
        if qty is not None:
            order_placement = (campaign_product, qty)
            print(campaign_product['name'])
            break

    if not order_placement:
        print('no order_placement')
        return

    # temperory solution
    # if platform_name == 'instagram':
    #     pre_order = db.api_pre_order.find_one(
    #         {'customer_name': comment['customer_name'], 'campaign_id': campaign['id'], 'platform': comment['platform']})
    # elif platform_name == 'youtube':
    #     pre_order = db.api_pre_order.find_one(
    #         {'customer_name': comment['customer_name'], 'campaign_id': campaign['id'], 'platform': comment['platform']})

    else:
        pre_order = db.api_pre_order.find_one(
            {'customer_id': comment['customer_id'], 'campaign_id': campaign['id'], 'platform': comment['platform']})

    if not pre_order:
        print("creating pre_order")
        increment_id = get_incremented_filed(
            collection_name="api_pre_order", field_name="id")

        print(f"increment_id {increment_id}")
        print(f"type of increment_id: {type(increment_id)}")

        template = api_pre_order_template.copy()
        template.update({
            "id": increment_id,
            'customer_id': comment['customer_id'],
            'customer_name': comment['customer_name'],
            'customer_img': comment['image'],
            'campaign_id': campaign['id'],
            'platform': comment['platform'],
            'platform_id': platform['id'],
            'created_at': datetime.utcnow()
        })

        try:
            _id = db.api_pre_order.insert_one(template).inserted_id
            pre_order = db.api_pre_order.find_one(_id)
        except Exception as e:
            print(e)
            print('new pre_order error!!!!!')
            return

    state = PreOrderHelper.add_or_update_by_comment(
        pre_order, order_placement[0], order_placement[1])

    if not state:
        print('no state')
        return
    print(f"state: {state}")
    comment_responding(platform_name, platform, campaign, pre_order,
                       comment, campaign_product, qty, state)


def command_responding(platform_name, platform, campaign, comment, command):
    # return
    if platform_name == 'facebook':
        text = i18n_get_comment_command_response(
            campaign, comment, command, lang=platform['lang'])
        api_fb_post_page_message_on_comment(
            platform['token'], comment['id'], text)
    elif platform_name == 'youtube':
        return
    elif platform_name == 'instagram':
        return


def comment_responding(platform_name, platform, campaign, pre_order, comment, campaign_product, qty, state):
    # return
    if platform_name == 'facebook':
        text = i18n_get_request_response(
            state, campaign_product, qty, lang=platform['lang'])

        shopping_cart_info, info_in_pm_notice = i18n_get_additional_text(pre_order,
                                                                         lang=platform['lang'])
        code, ret = api_fb_post_page_comment_on_comment(
            platform['token'], comment['id'], text+info_in_pm_notice)

        print("code", code)
        print("response", ret)
        api_fb_post_page_message_on_comment(
            platform['token'], comment['id'], text+shopping_cart_info)
    elif platform_name == 'youtube':
        text = i18n_get_request_response(
        state, campaign_product, qty, lang=platform['lang'])

        shopping_cart_info, info_in_pm_notice = i18n_get_additional_text(pre_order,
                                                                         lang=platform['lang'])
        

        customer_name =comment['customer_name']
        text = f"@{customer_name}"+ text+f"Shopping Cart: {settings.WEB_SERVER_URL}/buyer/cart/{pre_order['id']}"
        live_chat_id = comment.get("live_chat_id")
        if not live_chat_id:
            return


        # access_token = platform.get('page_token')

        youtube_campaign = campaign['youtube_campaign']
        access_token = youtube_campaign.get('access_token')
        if not access_token :
            print("no access token")
            return
        code, ret = api_youtube_post_live_chat_comment(access_token, live_chat_id, text)

        print(f"youtube post comment response code: {code}")
        print(ret)
    elif platform_name == 'instagram':
        return
