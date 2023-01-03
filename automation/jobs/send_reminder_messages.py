import os
import config
import django

from lib.i18n.reminder_message import get_uncheckout_cart_reminder_message

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
def send_reminder_messages_job(pymongo_cart, user_subscription_id, lang="en"):
    sender_id = pymongo_cart['customer_id']
    user_subscription_data = database.lss.user_subscription.UserSubscription.get(id=user_subscription_id)
    plugins = user_subscription_data.get('user_plan',{}).get('plugins')
    link = __get_link(pymongo_cart, plugins)
    message = get_uncheckout_cart_reminder_message(link, lang=lang)
    if sender_id in [None,""]:
        return False
    if pymongo_cart['platform'] not in ["facebook", "instagram"]:
        return False
    if pymongo_cart['platform'] == "facebook":
        facebook_page = database.lss.facebook_page.FacebookPage.get(id=pymongo_cart['platform_id'])
        service.facebook.chat_bot.post_page_text_message_chat_bot(facebook_page['token'], sender_id, message)
    if pymongo_cart['platform'] == "instagram":
        instagram_profile = database.lss.instagram_profile.InstagramProfile.get(id=pymongo_cart['platform_id'])
        service.instagram.chat_bot.post_page＿text_message_chat_bot(instagram_profile['connected_facebook_page_id'], instagram_profile['token'], sender_id, message)
def __get_link(pymongo_cart, plugins=None):
    if plugins:
        if lss_plugins.easy_store.EASY_STORE in plugins:
            return settings.SHOPPING_CART_RECAPTCHA_URL + lss_plugins.easy_store.EASY_STORE + '/' + str(pymongo_cart['_id'])
        elif lss_plugins.ordr_startr.ORDR_STARTR in plugins:
            return settings.SHOPPING_CART_RECAPTCHA_URL + lss_plugins.ordr_startr.ORDR_STARTR + '/' + str(pymongo_cart['_id'])
        elif lss_plugins.shopify.SHOPIFY in plugins:
            return settings.SHOPPING_CART_URL + '/' + str(pymongo_cart['_id'])

        return settings.SHOPPING_CART_URL + '/' + str(pymongo_cart['_id'])
    else:
        return settings.SHOPPING_CART_URL + '/' + str(pymongo_cart['_id'])
