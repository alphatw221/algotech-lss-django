import os
import django
try:
    os.environ['DJANGO_SETTINGS_MODULE']='lss.settings' #for rq_job
    django.setup()
except Exception as e:
    print(e)
from backend.utils.text_processing.command_processor import \
    CommandTextProcessor
from backend.utils.text_processing.order_code_processor import \
    OrderCodeTextProcessor
from backend.i18n.comment_command import i18n_get_comment_command_response
# from backend.i18n.campaign_announcement 
# from backend.i18n.cart_product_request import (i18n_get_additional_text,
#                                                i18n_get_request_response)
from backend.api.facebook.post import (api_fb_post_page_comment_on_comment,
                                       api_fb_post_page_message_on_comment)
from api.models.order.pre_order import api_pre_order_template
# from api.models.campaign.campaign_comment import CampaignComment
# from api.models.campaign.campaign import Campaign

from backend.pymongo.mongodb import db, client, get_incremented_filed
from datetime import datetime

def comment_job(campaign, platform_name, platform, comment, order_codes_mapping):
    # print(
    #     f"campaign_id: {campaign['id']}, \
    #     comment_id:{comment['id']},\
    #     message:{comment['message']},\
    #     commented_at:{comment['created_time']},\
    #     customer_id:{comment['customer_id']},\
    #     customer_name:{comment['customer_name']}"
    # )
    command = CommandTextProcessor.process(comment['message'])
    if command:
        text = i18n_get_comment_command_response(
                    campaign, comment, command, lang=platform['lang'])
        api_fb_post_page_message_on_comment(
            platform['token'], comment['id'], text)
        return

    order_placement={}
    for order_code, campaign_product in order_codes_mapping.items():
        qty = OrderCodeTextProcessor.process(comment['message'], order_code)
        if qty is not None:
            order_placement[campaign_product['id']]=(campaign_product,qty)

    # #TODO check qty
    if order_placement:
        try:
            pre_order = db.api_pre_order.find_one({'customer_id':comment['customer_id'],'campaign_id':comment['campaign_id'],'platform':comment['platform']})
        except Exception as e:  # TODO NOT FOUND
            increased_id=get_incremented_filed()
            api_pre_order_template.update({
                "id": increased_id,
                'customer_id':comment['customer_id'],
                'campaign_id':comment['campaign_id'],
                'platform':comment['platform']
            })
            _id=db.api_pre_order.insert_one(api_pre_order_template)
            pre_order = db.api_pre_order.find_one({'_id': _id})

    # for campaign_product_id, product_qty in order_placement.items():
    #     if not campaign_product['status']:
    #         RequestState.INVALID_PRODUCT_NOT_ACTIVATED
    #         return
    #     if campaign_product['max_order_amount'] and \
    #             product_qty[1] > campaign_product['max_order_amount']:
    #         RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT
    #         return

        
    #         existing_cart_product = CartProductManager.get_last_valid_cart_product(
    #             request.campaign,
    #             item.campaign_product,
    #             request.customer_id,
    #             request.platform,
    #         )
    #         if not existing_cart_product:
    #             if item.qty == 0:
    #                 item.state = RequestState.INVALID_ADD_ZERO_QTY
    #             else:
    #                 item.state = RequestState.ADDING
    #         else:
    #             item.orig_cart_product = existing_cart_product
    #             if item.qty > 0:
    #                 if not item.campaign_product.customer_editable:
    #                     item.state = RequestState.INVALID_EDIT_NOT_ALLOWED
    #                 else:
    #                     item.state = RequestState.UPDATING
    #             elif item.qty == 0:
    #                 if not item.campaign_product.customer_removable:
    #                     item.state = RequestState.INVALID_REMOVE_NOT_ALLOWED
    #                 else:
    #                     item.state = RequestState.DELETING
    #             else:
    #                 item.state = RequestState.INVALID_UNKNOWN_REQUEST


    # text = i18n_get_request_response(
    #             self.request, lang=self.facebook_page.lang)

    # shopping_cart_info, info_in_pm_notice = i18n_get_additional_text(
    #     lang=self.facebook_page.lang)

    # api_fb_post_page_comment_on_comment(
    #         page_token, comment_id, message_text)

    # api_fb_post_page_message_on_comment(
    #         platform['token'], comment['id'], text)
