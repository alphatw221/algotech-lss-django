import os
import config
import django

try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS  # for rq_job
    django.setup()
except Exception:
    pass

from django.conf import settings
from backend.utils.text_processing.command_processor import \
    CommandTextProcessor
from backend.utils.text_processing.order_code_processor import \
    OrderCodeTextProcessor

import lib
import database
import service

@lib.error_handle.error_handler.comment_job_error_handler.comment_job_error_handler
def comment_job(campaign_data, user_subscription_data, platform_name, platform_instance_data, comment, order_codes_mapping):
    logs=[]

    logs.append(["platform",platform_name])
    logs.append(["message",comment['message']])

    command = CommandTextProcessor.process(comment['message'])
    if command:
        logs.append(["action",'command'])
        command_responding(platform_name, platform_instance_data,
                           campaign_data, user_subscription_data, comment, command)
        lib.util.logger.print_table(["Campaign ID", campaign_data.get('id')],logs)
        return

    order_placement = None
    for order_code, campaign_product in order_codes_mapping.items():
        qty = OrderCodeTextProcessor.process(
            comment['message'], order_code)
        if qty is not None:
            order_placement = (campaign_product, qty)
            logs.append(["action",'order_placement'])
            logs.append(["order_code",order_code])
            break

    if not order_placement:
        logs.append(["action",'no order_placement'])
        lib.util.logger.print_table(["Campaign ID", campaign_data.get('id')],logs)
        return

    pre_order = database.lss.pre_order.PreOrder.get_object(customer_id= comment['customer_id'], campaign_id= campaign_data['id'], platform= comment['platform'])

    if not pre_order:
        pre_order = database.lss.pre_order.PreOrder.create_object(
            customer_id= comment['customer_id'],
            customer_name= comment['customer_name'],
            customer_img= comment['image'],
            campaign_id= campaign_data['id'],
            platform= comment['platform'],
            platform_id= platform_instance_data['id'],
        )

    state = lib.helper.order_helper.PreOrderHelper.add_or_update_by_comment(
        pre_order, order_placement[0], order_placement[1])

    if not state:
        logs.append(["state",'no state'])
        lib.util.logger.print_table(["Campaign ID", campaign_data.get('id')],logs)
        return
    logs.append(["state",str(state)])
    comment_responding(platform_name, platform_instance_data, campaign_data, user_subscription_data, pre_order,
                       comment, campaign_product, qty, state)
    lib.util.logger.print_table(["Campaign ID", campaign_data.get('id')],logs)

def command_responding(platform_name, platform_instance_data, campaign_data, user_subscription_data, comment, command):
    # return
    if platform_name == 'facebook':

        text = lib.i18n.comment_command.get_comment_command_response(
            campaign_data, comment, command, lang=user_subscription_data.get('buyer_lang'))
        service.facebook.post.post_page_message_on_comment(platform_instance_data['token'], comment['id'], text)
    elif platform_name == 'youtube':
        return
    elif platform_name == 'instagram':
        return


def comment_responding(platform_name, platform_instance_data, campaign_data, user_subscription_data, pre_order, comment, campaign_product, qty, state):
    # return
    if platform_name == 'facebook':

        text = lib.i18n.cart_product_request.get_request_response(
            state, campaign_product, qty, lang=user_subscription_data.get('buyer_lang'))

        if state in [ lib.helper.order_helper.PreOrderHelper.RequestState.ADDED, 
            lib.helper.order_helper.PreOrderHelper.RequestState.UPDATED, 
            lib.helper.order_helper.PreOrderHelper.RequestState.DELETED]:
            
            shopping_cart_info, info_in_pm_notice = lib.i18n.cart_product_request.get_additional_text(pre_order, lang=user_subscription_data.get('buyer_lang'))
        else:
            shopping_cart_info, info_in_pm_notice = "", ""
        code, ret = service.facebook.post.post_page_comment_on_comment( platform_instance_data['token'], comment['id'], text+info_in_pm_notice)
        if code!=200:
            print("response", ret)
        code, ret = service.facebook.post.post_page_message_on_comment(platform_instance_data['token'], comment['id'], text+shopping_cart_info)
        if code!=200:
            print("response", ret)
        
    elif platform_name == 'youtube':
        text = lib.i18n.cart_product_request.get_request_response(
        state, campaign_product, qty, lang=user_subscription_data.get('buyer_lang'))

        shopping_cart_info, info_in_pm_notice = lib.i18n.cart_product_request.get_additional_text(pre_order,
                                                                         lang=user_subscription_data.get('buyer_lang'))
        

        customer_name =comment['customer_name']
        link = settings.SHOPPING_CART_URL + '/' + str(pre_order._id)
        text = f"@{customer_name}"+ text+f"Shopping Cart: {link}"
        live_chat_id = comment.get("live_chat_id")
        
        if not live_chat_id:
            return

        access_token = platform_instance_data.get('token')
        if not access_token :
            print("no access token")
            return
        code, ret = service.youtube.live_chat.post_live_chat_comment(access_token, live_chat_id, text)
        if code!=200:
            print("response", ret)

    elif platform_name == 'instagram':
        text = lib.i18n.cart_product_request.get_request_response(
            state, campaign_product, qty, lang=user_subscription_data.get('buyer_lang'))

        shopping_cart_info, info_in_pm_notice = lib.i18n.cart_product_request.get_additional_text(pre_order,
                                                                         lang=user_subscription_data.get('buyer_lang'))
       
        code, ret =service.instagram.post.private_message( platform_instance_data['token'], comment['id'], text+shopping_cart_info)
        if code!=200:
            print("response", ret)
