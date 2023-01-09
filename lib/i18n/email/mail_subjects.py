from lib.i18n._i18n import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _

@lang_translate_default_en
def cart_checkout_mail_subject(order, lang=None):
    return _('EMAIL/ORDER_PLACED/SUBJECT{order_id}{campaign_title}'
    ).format(order_id=order.id, campaign_title=order.campaign.title)

@lang_translate_default_en
def order_confirm_mail_subject(order, lang=None):
    return _(
        'EMAIL/ORDER_CONFIRM/SUBJECT{order_id}{campaign_title}'
    ).format(order_id=order.id, campaign_title=order.campaign.title)
