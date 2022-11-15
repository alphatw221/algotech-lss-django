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
import plugins as lss_plugins

@lib.error_handle.error_handler.comment_job_error_handler.comment_job_error_handler
def send_reminder_messages_job(cart):
    sender_id = cart.customer_id
    user_subscription_data = database.lss.user_subscription.UserSubscription.get(id=cart.campaign.user_subscription.id)
    plugins = user_subscription_data.get('user_plan',{}).get('plugins')
    pymongo_cart = database.lss.cart.Cart.get_object(id=cart.id)
    link = __get_link(pymongo_cart, plugins)
    message = f"Live Show Seller: Your shopping cart is not checked out yet, shopping cart link: {link}"
    if sender_id in [None,""]:
        return False
    if cart.platform not in ["facebook", "instagram"]:
        return False
    if cart.platform == "facebook":
        print("facebook")
        facebook_page = database.lss.facebook_page.FacebookPage.get(id=cart.platform_id)
        print(facebook_page)
        service.facebook.chat_bot.post_page_text_message_chat_bot(facebook_page.token, sender_id, message)
    if cart.platform == "instagram":
        instagram_profile = database.lss.instagram_profile.InstagramProfile.get(id=cart.platform_id)
        service.instagram.chat_bot.post_page＿text_message_chat_bot(instagram_profile.connected_facebook_page_id, instagram_profile.token, sender_id, message)
def __get_link(pre_order, plugins=None):
    if plugins:
        if lss_plugins.easy_store.EASY_STORE in plugins:
            return settings.SHOPPING_CART_RECAPTCHA_URL + f'/{lss_plugins.easy_store.EASY_STORE}/{str(pre_order._id)}'
        elif lss_plugins.ordr_startr.ORDR_STARTR in plugins:
            return settings.SHOPPING_CART_RECAPTCHA_URL + f'/{lss_plugins.ordr_startr.ORDR_STARTR}/{str(pre_order._id)}'
        elif lss_plugins.shopify.SHOPIFY in plugins:
            return settings.SHOPPING_CART_URL + '/' + str(pre_order._id)

        return settings.SHOPPING_CART_URL + '/' + str(pre_order._id)
    else:
        return settings.SHOPPING_CART_URL + '/' + str(pre_order._id)
