from django.utils.translation import ugettext as _
from ._i18n import lang_translate_default_en

@lang_translate_default_en
def get_campaign_announcement_product_closed(order_code: str, lang=None):
    return _(
        'PRODUCT_CLOSED{order_code}'
    ).format(order_code=order_code)


@lang_translate_default_en
def get_campaign_announcement_product_sold_out(order_code: str, lang=None):
    return _(
        'PRODUCT_SOLD_OUT{order_code}'
    ).format(order_code=order_code)


@lang_translate_default_en
def get_campaign_announcement_lucky_draw_winner(product_name: str, customer_name: str, lang=None):
    return _(
        'LUCKY_DRAW_WINNER{customer_name}{product_name}'
    ).format(product_name=product_name,
             customer_name=customer_name)


@lang_translate_default_en
def get_campaign_announcement_quiz_game_winner(product_name: str, customer_name: str, lang=None):
    return _(
        'QUIZ_GAME_WINNER{customer_name}{product_name}'
    ).format(product_name=product_name, customer_name=customer_name)