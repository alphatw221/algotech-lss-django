from django.utils import translation
from django.utils.translation import gettext as _
from backend.i18n._helper import lang_translate_default_en


@lang_translate_default_en
def i18n_get_reset_password_mail_subject(lang=None):
    return  _('EMAIL/PASSWORD_RESET_LINK/SUBJECT')

@lang_translate_default_en
def i18n_get_reset_password_success_mail_subject(lang=None):
    return  _('EMAIL/PASSWORD_RESET_SUCCESS/SUBJECT')

@lang_translate_default_en
def i18n_get_verify_code_subject(lang=None):
    return  _('EMAIL/VERIFY/SUBJECT')

@lang_translate_default_en
def i18n_get_notify_wishlist_subject(lang=None):
    return _('EMAIL/WISHLIST/SUBJECT')

def get_foo_subject():
    return "123"