from backend.i18n._helper import lang_translate_default_en
from django.utils.translation import ugettext as _


@lang_translate_default_en
def i18n_get_command_command_order(delivery: str, option: str, total: str, link: str, dollar_sign: str,
                                   lang=None):
    text = [_('MESSAGE_HEADER'), '\n-----\n']
    text.extend(_i18n_get_order_items())
    text.append(_('DELIVERY{dollar_sign}{delivery}'
                  ).format(delivery=delivery))
    text.append('\n')
    text.append(_('OPTION{dollar_sign}{option}'
                  ).format(option=option))
    text.append('\n')
    text.append(_('TOTAL{dollar_sign}{total}'
                  ).format(total=total))
    text.append('\n')
    text.append(_('DETAIL{link}'
                  ).format(link=link))

    return ''.join(text
                   ).format(dollar_sign=dollar_sign)


def _i18n_get_order_items():
    return [
        _('ITEM_INFO{name}{qty}{dollar_sign}{total}'), '\n'
    ]
