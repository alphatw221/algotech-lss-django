from decimal import Decimal

import database


from ._i18n import lang_translate_default_en
from backend.utils.text_processing.command_processor import Command
from django.conf import settings
from django.utils.translation import ugettext as _
# from backend.pymongo.mongodb import db

@lang_translate_default_en
def get_uncheckout_cart_reminder_message(link:str, lang='en'):

    return _(
        'UNCHECKOUT_CART_REMINDER{link}'
    ).format(link=link)