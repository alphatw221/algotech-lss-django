from django.utils.translation import gettext as _
from backend.i18n._helper import lang_translate_default_en

@lang_translate_default_en
def i18n_get_verify_code_subject(lang=None):
    return  _('EMAIL/VERIFY/SUBJECT')