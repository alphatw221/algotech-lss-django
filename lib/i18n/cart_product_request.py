
from ._i18n import lang_translate_default_en
from django.conf import settings
from django.utils.translation import ugettext as _
import lib
from..helper.order_helper import RequestState
import plugins

@lang_translate_default_en
def get_request_response(state, api_campaign_product, qty, lang=None):
    output = [_('MESSAGE_PREFIX')]
    output.extend(get_response_content(state, api_campaign_product, qty))

    return ''.join(output)


@lang_translate_default_en
def get_plugins_additional_text(pre_order, _plugins:dict, lang=None):

    if plugins.easy_store.EASY_STORE in _plugins:
        
        link = settings.SHOPPING_CART_RECAPTCHA_URL + f'/{plugins.easy_store.EASY_STORE}/{str(pre_order._id)}'
    
        shopping_cart_info = _('SHOPPING_CART_INFO{link}'
                            ).format(link=link)
        more_info_in_pm_notice = _('MORE_INFO_IN_PM_NOTICE')

        return shopping_cart_info, more_info_in_pm_notice
    elif plugins.ordr_startr.ORDR_STARTR in _plugins:
        link = settings.SHOPPING_CART_RECAPTCHA_URL + f'/{plugins.ordr_startr.ORDR_STARTR}/{str(pre_order._id)}'
    
        shopping_cart_info = _('SHOPPING_CART_INFO{link}'
                            ).format(link=link)
        more_info_in_pm_notice = _('MORE_INFO_IN_PM_NOTICE')

        return shopping_cart_info, more_info_in_pm_notice
    elif plugins.shopify.SHOPIFY in _plugins:
        link = settings.SHOPPING_CART_URL + '/' + str(pre_order._id) + '/' + plugins.shopify.SHOPIFY
    
        shopping_cart_info = _('SHOPPING_CART_INFO{link}'
                            ).format(link=link)
        more_info_in_pm_notice = _('MORE_INFO_IN_PM_NOTICE')

        return shopping_cart_info, more_info_in_pm_notice
    else:
        return get_additional_text(pre_order, lang=lang)


@lang_translate_default_en
def get_additional_text(pre_order, lang=None):

    #link = settings.SHOPPING_CART_RECAPTCHA_URL + '/' + type + '/' + object_id
    link = settings.SHOPPING_CART_URL + '/' + str(pre_order._id)
    
    shopping_cart_info = _('SHOPPING_CART_INFO{link}'
                           ).format(link=link)
    more_info_in_pm_notice = _('MORE_INFO_IN_PM_NOTICE')
    return shopping_cart_info, more_info_in_pm_notice


def get_response_content(state, api_campaign_product, qty):

    if state == RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT:
        return _('INVALID_EXCEED_MAX_ORDER_AMOUNT{order_code}{max_order_amount}').format(
            order_code=api_campaign_product['order_code'],
            max_order_amount=api_campaign_product['max_order_amount'],
        )
    else:
        if state == RequestState.ADDED:
            result = _('ADDED')
        elif state == RequestState.UPDATED:
            result = _('UPDATED')
        elif state == RequestState.DELETED:
            result = _('DELETED')
        elif state == RequestState.INSUFFICIENT_INV:
            result = _('INSUFFICIENT_INV')
        elif state == RequestState.INVALID_PRODUCT_NOT_ACTIVATED:
            result = _('INVALID_PRODUCT_NOT_ACTIVATED')
            return _('ITEM_INFO{order_code}{result}').format(
                order_code=api_campaign_product['order_code'],
                result=result
            )
        elif state == RequestState.INVALID_REMOVE_NOT_ALLOWED:
            result = _('INVALID_REMOVE_NOT_ALLOWED')
        elif state == RequestState.INVALID_EDIT_NOT_ALLOWED:
            result = _('INVALID_EDIT_NOT_ALLOWED')
        elif state == RequestState.INVALID_ADD_ZERO_QTY:
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
        if item.state == RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT:
            items_info.append(
                _('INVALID_EXCEED_MAX_ORDER_AMOUNT{order_code}{max_order_amount}').format(
                    order_code=item.campaign_product.order_code,
                    max_order_amount=item.campaign_product.max_order_amount,
                )
            )
        else:
            if item.state == RequestState.ADDED:
                result = _('ADDED')
            elif item.state == RequestState.UPDATED:
                result = _('UPDATED')
            elif item.state == RequestState.DELETED:
                result = _('DELETED')
            elif item.state == RequestState.INSUFFICIENT_INV:
                result = _('INSUFFICIENT_INV')
            elif item.state == RequestState.INVALID_PRODUCT_NOT_ACTIVATED:
                result = _('INVALID_PRODUCT_NOT_ACTIVATED')
            elif item.state == RequestState.INVALID_REMOVE_NOT_ALLOWED:
                result = _('INVALID_REMOVE_NOT_ALLOWED')
            elif item.state == RequestState.INVALID_EDIT_NOT_ALLOWED:
                result = _('INVALID_EDIT_NOT_ALLOWED')
            elif item.state == RequestState.INVALID_ADD_ZERO_QTY:
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
