
from ._i18n import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _

@lang_translate_default_en
def get_uncheckout_cart_reminder_message(link:str, lang='en'):

    return _(
        'UNCHECKOUT_CART_REMINDER{link}'
    ).format(link=link)