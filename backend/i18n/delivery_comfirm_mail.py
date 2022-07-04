from math import prod
from backend.i18n._helper import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _


@lang_translate_default_en
def i18n_get_mail_content(order_id, campaign_data, order_data, shop_name, lang=None):
    meta = order_data['meta']
    products = order_data['products']
    campaign_title = campaign_data['title']
    meta_logistic = campaign_data['meta_logistic']

    mail_content = f'<h3>Order # {str(order_id)}</h3>'

    return mail_content


@lang_translate_default_en
def i18n_get_mail_subject(shop_name, lang=None):
    mail_subject = '[LSS] '+ shop_name + ' order confirmation'
    return mail_subject