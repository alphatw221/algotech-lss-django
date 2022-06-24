from ._recaptcha_api_caller import RecaptchaApiCaller
from django.conf import settings


def verify_token(token: str):
    params={
        'secret':settings.RECAPTCHA_SECRET_KEY,
        'response':token
    }
    ret = RecaptchaApiCaller('',params=params).post()
    return ret

