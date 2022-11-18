import os
import config
import django

try:
    os.environ['DJANGO_SETTINGS_MODULE'] = config.DJANGO_SETTINGS  # for rq_job
    django.setup()
except Exception:
    pass

from django.conf import settings
import lib
import database
import service
import plugins as lss_plugins

@lib.error_handle.error_handler.comment_job_error_handler.comment_job_error_handler
def comment_job(campaign_data, user_subscription_data, platform_name, platform_instance_data, comment, order_codes_mapping):
    logs=[]

    logs.append(["platform",platform_name])
    logs.append(["message",comment['message']])

    order_placement = None
    match_keyword = False

    for order_code, campaign_product in order_codes_mapping.items():
        qty = lib.util.text_processor.OrderCodeTextProcessor.process(comment['message'], order_code)
        if qty is not None:
            order_placement = (campaign_product, qty)
            logs.append(["action",'order_placement'])
            logs.append(["order_code",order_code])
            break

    if not order_placement:
        logs.append(["action",'no order_placement'])

        comment_auto_reply = campaign_data.get('meta',{}).get('comment_auto_reply',{})
        if comment_auto_reply and comment_auto_reply.get('input_msg'):
            for keyword in comment_auto_reply.get('input_msg').split(','):
                if keyword in comment['message']:
                    match_keyword = True
                    break
        
        if match_keyword:
            __demo_responding(platform_name, platform_instance_data, campaign_data, user_subscription_data, comment)
        else:
            logs.append(["action",'no matched keyword'])
            lib.util.logger.print_table(["Campaign ID", campaign_data.get('id')],logs)
            return
        
    pymongo_cart = database.lss.cart.Cart.get_object(customer_id= comment['customer_id'], campaign_id= campaign_data['id'], platform= comment['platform'])

    if not pymongo_cart:
        pymongo_cart = database.lss.cart.Cart.create_object(
            customer_id= comment['customer_id'],
            customer_name= comment['customer_name'],
            customer_img= comment['image'],
            campaign_id= campaign_data['id'],
            user_subscription_id = campaign_data['user_subscription_id'],
            platform= comment['platform'],
            platform_id= platform_instance_data.get('id'),
            meta = {'comment':comment}      # for ordr_startr might be useful for other integration
        )

    campaign_product_data = order_placement[0]
    qty = order_placement[1]

    state = lib.helper.cart_helper.CartHelper.update_cart_product_by_comment(pymongo_cart, campaign_product_data, qty)

    if not state:
        logs.append(["state",'no state'])
        lib.util.logger.print_table(["Campaign ID", campaign_data.get('id')],logs)
        return
    logs.append(["state",str(state)])
    __comment_responding(platform_name, platform_instance_data, campaign_data, user_subscription_data, pymongo_cart,
                       comment, campaign_product, qty, state)
    lib.util.logger.print_table(["Campaign ID", campaign_data.get('id')],logs)


def __comment_responding(platform_name, platform_instance_data, campaign_data, user_subscription_data, pymongo_cart, comment, campaign_product, qty, state):
    
    plugins = user_subscription_data.get('user_plan',{}).get('plugins')
    link = __get_link(pymongo_cart, plugins)
    
    _, private_message = __get_comment_and_private_message( pymongo_cart, campaign_data, state, campaign_product, qty, link, plugins)
    if platform_name == 'facebook':

        # if state == lib.helper.order_helper.RequestState.INSUFFICIENT_INV:    
        #     code, ret = service.facebook.post.post_page_comment_on_comment( platform_instance_data.get('token'), comment['id'], comment_message)
        #     if code!=200:
        #         print("response", ret)

        if 'facebook_buttons' in campaign_data.get('meta_reply',{}):
            facebook_buttons = campaign_data.get('meta_reply',{}).get('facebook_buttons',[])
            private_message = private_message.replace('[LINK]','')
            view_order_button =  {
                "type":"web_url",
                "url":link,
                "title":"View Order"
            }
            facebook_buttons.insert(0,view_order_button)    # for ordr_startr 

            code, ret = service.facebook.message.send_private_message_with_buttons(platform_instance_data.get('token'), comment['id'], private_message, facebook_buttons)
            if code!=200:
                print("response", ret)
            return
        private_message = private_message.replace('[LINK]', link)
        code, ret = service.facebook.post.post_page_message_on_comment(platform_instance_data.get('token'), comment['id'], private_message)
        if code!=200:
            print("response", ret)
        
    elif platform_name == 'youtube':
        private_message = private_message.replace('[LINK]',link)
        customer_name =comment['customer_name']
        text = f"@{customer_name}"+ private_message
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
        private_message = private_message.replace('[LINK]',link)
        code, ret =service.instagram.post.private_message( platform_instance_data.get('token'), comment['id'], private_message)
        if code!=200:
            print("response", ret)
    
    elif platform_name == 'twitch':
        private_message = private_message.replace('[LINK]',link)
        code, ret = service.twitch.twitch.whisper_to_user(platform_instance_data.get('token'), platform_instance_data.get('user_name'), comment['customer_id'], private_message)
        if code!=200:
            print("response", ret)

    elif platform_name == 'tiktok':
        pass





def __demo_responding(platform_name, platform_instance_data, campaign_data, user_subscription_data, comment):
    
    private_message = campaign_data.get('meta',{}).get('comment_auto_reply',{}).get('output_msg','')
    private_message.replace('[NAME]', comment['customer_name'])
    if platform_name == 'facebook':

        code, ret = service.facebook.post.post_page_message_on_comment(platform_instance_data.get('token'), comment['id'], private_message)
        if code!=200:
            print("response", ret)
        
    elif platform_name == 'youtube':

        customer_name =comment['customer_name']
        text = f"@{customer_name}"+ private_message
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

        code, ret =service.instagram.post.private_message( platform_instance_data.get('token'), comment['id'], private_message)
        if code!=200:
            print("response", ret)
    
    elif platform_name == 'twitch':
        
        code, ret = service.twitch.twitch.whisper_to_user(platform_instance_data.get('token'), platform_instance_data.get('user_name'), comment['customer_id'], private_message)
        if code!=200:
            print("response", ret)

    elif platform_name == 'tiktok':
        pass

def __get_comment_and_private_message( pymongo_cart, campaign_data, state, campaign_product, qty, link, plugins):


    if state in campaign_data.get('meta_reply',{}):
        reply_message = campaign_data.get('meta_reply',{}).get(state)
        # reply_message = reply_message.replace('[LINK]',link)
        reply_message = reply_message.replace('[PRODUCT_NAME]', campaign_product.get('name',''))
        #reply_message = reply_message.replace('[ORDER_CODE]', campaign_product.get('order_code'))
        description = campaign_product.get('description') if campaign_product.get('description') else ''
        reply_message = reply_message.replace('[DESCRIPTION]', description)
        # reply_message.replace('[QTY]', str(qty))
        return "", reply_message

    if plugins:
        shopping_cart_info, info_in_pm_notice = lib.i18n.cart_product_request.get_plugins_additional_text(pymongo_cart, plugins, lang=campaign_data.get('lang'))
    else:
        shopping_cart_info, info_in_pm_notice = lib.i18n.cart_product_request.get_additional_text(pymongo_cart, lang=campaign_data.get('lang'))

    if state not in [ lib.helper.order_helper.RequestState.ADDED, 
            lib.helper.order_helper.RequestState.UPDATED, 
            lib.helper.order_helper.RequestState.DELETED]:
            shopping_cart_info, info_in_pm_notice = "", ""
    
    text = lib.i18n.cart_product_request.get_request_response(
            state, campaign_product, qty, lang=campaign_data.get('lang'))
    return text+info_in_pm_notice, text+shopping_cart_info


def __get_link(pymongo_cart, plugins=None):
    if plugins:
        if lss_plugins.easy_store.EASY_STORE in plugins:
            return settings.SHOPPING_CART_RECAPTCHA_URL + f'/{lss_plugins.easy_store.EASY_STORE}/{str(pymongo_cart._id)}'
        elif lss_plugins.ordr_startr.ORDR_STARTR in plugins:
            return settings.SHOPPING_CART_RECAPTCHA_URL + f'/{lss_plugins.ordr_startr.ORDR_STARTR}/{str(pymongo_cart._id)}'
        elif lss_plugins.shopify.SHOPIFY in plugins:
            return settings.SHOPPING_CART_URL + '/' + str(pymongo_cart._id)

        return settings.SHOPPING_CART_URL + '/' + str(pymongo_cart._id)
    else:
        return settings.SHOPPING_CART_URL + '/' + str(pymongo_cart._id)

    # {
    #     'added':'You successfully bidded for:\n [PRODUCT_NAME] - [DESCRIPTION]\n\nCut Off Time:Thursday, 25th August 2022, 12 noon!\n\nKindly click View Order and proceed to make payment before cut off time to secure your order.\n[LINK]',
    # }