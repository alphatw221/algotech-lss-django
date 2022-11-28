from django.utils.translation import gettext as _
from lib.i18n._i18n import lang_translate_default_en

@lang_translate_default_en
def i18n_get_notify_wishlist_subject(lang=None):
    return _('EMAIL/WISHLIST/SUBJECT')