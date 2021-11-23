from backend.i18n._helper import lang_kwarg_translate
from django.utils.translation import ugettext as _


@lang_kwarg_translate
def i18n_sample(items: tuple, lang=None):
    output = [_('Product details: ')]
    output.extend(i18n_get_items(items))
    return ''.join(output)


def i18n_get_items(items: tuple):
    result = []
    for item in items:
        result.append(
            _('Order code: {order_code}. Order quantity: {qty}. ').format(
                order_code=item[0],
                qty=item[1])
        )
    return result
