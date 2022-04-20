from math import prod
from backend.i18n._helper import lang_translate_default_en
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils import translation


@lang_translate_default_en
def i18n_get_register_confirm_mail_content(firstName, lastName,contactNumber, email, password, plan, period, country, lang=None):

    mail_content = ""
    return mail_content


@lang_translate_default_en
def i18n_get_register_confirm_mail_subject(lang=None):
    mail_subject = _('MAIL_SUBJECT_WELCOME')
    return mail_subject

@lang_translate_default_en
def i18n_get_register_activate_mail_subject(lang=None):
    mail_subject = _('MAIL_SUBJECT_ACTIVATION')
    return mail_subject