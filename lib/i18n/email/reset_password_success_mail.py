from django.utils import translation
from django.utils.translation import gettext as _
from .._i18n import lang_translate_default_en




@lang_translate_default_en
def i18n_get_mail_subject(lang=None):
    return  _('EMAIL/PASSWORD_RESET_SUCCESS/SUBJECT')
