from django.utils.translation import ugettext as _
from backend.i18n._helper import lang_kwarg_translate


@lang_kwarg_translate
def i18n_sample(items: tuple, lang=None):
    output = [_('Product added. Details: ')]
    for item in items:
        output.append(
            _('Order code: {order_code}. Order quantity: {qty}. ').format(
                order_code=item[0],
                qty=item[1])
        )
    return ''.join(output)
