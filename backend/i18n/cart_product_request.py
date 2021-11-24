from backend.cart.cart_product.request import CartProductRequest, RequestState
from backend.i18n._helper import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _


@lang_translate_default_en
def i18n_get_request_response(request: CartProductRequest, lang=None):
    output = [_('MESSAGE_PREFIX')]
    output.extend(_i18n_get_items_info(request))

    return ''.join(output)


@lang_translate_default_en
def i18n_get_additional_text(lang=None):
    shopping_cart_info = _('SHOPPING_CART_INFO{link}'
                           ).format(link=settings.SHOPPING_CART_URL)
    more_info_in_pm_notice = _('MORE_INFO_IN_PM_NOTICE')
    return shopping_cart_info, more_info_in_pm_notice


def _i18n_get_items_info(request: CartProductRequest):
    return [_(
            'ITEM_INFO{order_code}{qty}{result}'
            ).format(order_code=item.campaign_product.order_code,
                     qty=item.qty,
                     result=_i18n_get_item_result_text(item.state),
                     max_order_amount=item.campaign_product.max_order_amount)
            for item in request.get_items()]


def _i18n_get_item_result_text(state: RequestState):
    if state == RequestState.ADDED:
        return _('ADDED')
    elif state == RequestState.UPDATED:
        return _('UPDATED')
    elif state == RequestState.DELETED:
        return _('DELETED')
    elif state == RequestState.INSUFFICIENT_INV:
        return _('INSUFFICIENT_INV')
    elif state == RequestState.INVALID_PRODUCT_NOT_ACTIVATED:
        return _('INVALID_PRODUCT_NOT_ACTIVATED')
    elif state == RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT:
        return _('INVALID_EXCEED_MAX_ORDER_AMOUNT')
    elif state == RequestState.INVALID_REMOVE_NOT_ALLOWED:
        return _('INVALID_REMOVE_NOT_ALLOWED')
    elif state == RequestState.INVALID_EDIT_NOT_ALLOWED:
        return _('INVALID_EDIT_NOT_ALLOWED')
    elif state == RequestState.INVALID_ADD_ZERO_QTY:
        return _('INVALID_ADD_ZERO_QTY')
    else:
        return _('N/A')
