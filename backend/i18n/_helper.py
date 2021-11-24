from django.utils import translation


def lang_kwarg_translate(func):
    def wrapper(*args, **kwargs):
        lang = kwargs['lang'] if 'lang' in kwargs else 'en'
        with translation.override(lang):
            return func(*args, **kwargs)
    return wrapper
