from django.utils.translation import gettext as _





def i18n_get_reset_password_mail_subject(lang=None):
    return  _('EMAIL/PASSWORD_RESET_LINK/SUBJECT')

def i18n_get_reset_password_success_mail_subject(lang=None):
    return  _('EMAIL/PASSWORD_RESET_SUCCESS/SUBJECT')


def get_foo_subject():
    return "123"