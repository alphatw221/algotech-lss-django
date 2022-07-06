
from ._i18n import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _
import lib

@lang_translate_default_en
def get_request_response(state, api_campaign_product, qty, lang=None):
    output = [_('MESSAGE_PREFIX')]
    output.extend(get_response_content(state, api_campaign_product, qty))

    return ''.join(output)


@lang_translate_default_en
def get_additional_text(pre_order, lang=None):

    link = settings.SHOPPING_CART_URL + '/' + str(pre_order._id)
    shopping_cart_info = _('SHOPPING_CART_INFO{link}'
                           ).format(link=link)
    more_info_in_pm_notice = _('MORE_INFO_IN_PM_NOTICE')
    return shopping_cart_info, more_info_in_pm_notice


def get_response_content(state, api_campaign_product, qty):

    if state == lib.helper.order_helper.PreOrderHelper.RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT:
        return _('INVALID_EXCEED_MAX_ORDER_AMOUNT{order_code}{max_order_amount}').format(
            order_code=api_campaign_product['order_code'],
            max_order_amount=api_campaign_product['max_order_amount'],
        )
    else:
        if state == lib.helper.order_helper.PreOrderHelper.RequestState.ADDED:
            result = _('ADDED')
        elif state == lib.helper.order_helper.PreOrderHelper.RequestState.UPDATED:
            result = _('UPDATED')
        elif state == lib.helper.order_helper.PreOrderHelper.RequestState.DELETED:
            result = _('DELETED')
        elif state == lib.helper.order_helper.PreOrderHelper.RequestState.INSUFFICIENT_INV:
            result = _('INSUFFICIENT_INV')
        elif state == lib.helper.order_helper.PreOrderHelper.RequestState.INVALID_PRODUCT_NOT_ACTIVATED:
            result = _('INVALID_PRODUCT_NOT_ACTIVATED')
        elif state == lib.helper.order_helper.PreOrderHelper.RequestState.INVALID_REMOVE_NOT_ALLOWED:
            result = _('INVALID_REMOVE_NOT_ALLOWED')
        elif state == lib.helper.order_helper.PreOrderHelper.RequestState.INVALID_EDIT_NOT_ALLOWED:
            result = _('INVALID_EDIT_NOT_ALLOWED')
        elif state == lib.helper.order_helper.PreOrderHelper.RequestState.INVALID_ADD_ZERO_QTY:
            result = _('INVALID_ADD_ZERO_QTY')
        else:
            result = _('N/A')

        return _('ITEM_INFO{order_code}{qty}{result}').format(
            order_code=api_campaign_product['order_code'],
            qty=qty,
            result=result
        )


def get_items_info(request):
    items_info = []
    for item in request.get_items():
        if item.state == lib.helper.order_helper.PreOrderHelper.RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT:
            items_info.append(
                _('INVALID_EXCEED_MAX_ORDER_AMOUNT{order_code}{max_order_amount}').format(
                    order_code=item.campaign_product.order_code,
                    max_order_amount=item.campaign_product.max_order_amount,
                )
            )
        else:
            if item.state == lib.helper.order_helper.PreOrderHelper.RequestState.ADDED:
                result = _('ADDED')
            elif item.state == lib.helper.order_helper.PreOrderHelper.RequestState.UPDATED:
                result = _('UPDATED')
            elif item.state == lib.helper.order_helper.PreOrderHelper.RequestState.DELETED:
                result = _('DELETED')
            elif item.state == lib.helper.order_helper.PreOrderHelper.RequestState.INSUFFICIENT_INV:
                result = _('INSUFFICIENT_INV')
            elif item.state == lib.helper.order_helper.PreOrderHelper.RequestState.INVALID_PRODUCT_NOT_ACTIVATED:
                result = _('INVALID_PRODUCT_NOT_ACTIVATED')
            elif item.state == lib.helper.order_helper.PreOrderHelper.RequestState.INVALID_REMOVE_NOT_ALLOWED:
                result = _('INVALID_REMOVE_NOT_ALLOWED')
            elif item.state == lib.helper.order_helper.PreOrderHelper.RequestState.INVALID_EDIT_NOT_ALLOWED:
                result = _('INVALID_EDIT_NOT_ALLOWED')
            elif item.state == lib.helper.order_helper.PreOrderHelper.RequestState.INVALID_ADD_ZERO_QTY:
                result = _('INVALID_ADD_ZERO_QTY')
            else:
                result = _('N/A')

            items_info.append(
                _('ITEM_INFO{order_code}{qty}{result}').format(
                    order_code=item.campaign_product.order_code,
                    qty=item.qty,
                    result=result
                )
            )
    return items_info
