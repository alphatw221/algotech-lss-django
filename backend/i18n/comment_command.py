from decimal import Decimal

from api.models.campaign.campaign_comment import CampaignComment
from api.models.cart.cart_product import CartProduct
from api.models.order.order import Order
from backend.i18n._helper import lang_translate_default_en
from backend.utils.text_processing.command_processor import Command
from django.conf import settings
from django.utils.translation import ugettext as _


@lang_translate_default_en
def i18n_get_comment_command_response(comment: CampaignComment, command: Command, lang=None):
    if command == Command.CART:
        return i18n_get_comment_command_cart(comment)
    if command == Command.ORDER:
        return i18n_get_comment_command_order(comment)
    return ''


def i18n_get_comment_command_cart(comment: CampaignComment):
    cart_products: CartProduct = CartProduct.objects.select_related('campaign_product').filter(
        campaign=comment.campaign, customer_id=comment.customer_id, status='valid')
    if not cart_products:
        return _('COMMENT_COMMAND_CART_NO_CART_PRODUCT')
    cart_products, subtotal = _i18n_get_cart_products(cart_products)

    text = [_('COMMENT_COMMAND_CART_MESSAGE_HEADER'), '\n-----\n']
    text.extend(cart_products)
    text.append(_('TOTAL{dollar_sign}{total}\n'
                  ).format(total=subtotal, dollar_sign=comment.campaign.currency_sign))
    text.append(_('DETAIL{link}\n'
                  ).format(link=settings.SHOPPING_CART_URL))

    return ''.join(text)


def _i18n_get_cart_products(cart_products: list[CartProduct]):
    items = []
    subtotal = 0
    count = len(cart_products)
    digits = len(str(count))
    for i, cart_product in enumerate(cart_products):
        name = getattr(cart_product.campaign_product, 'name', '')
        qty = getattr(cart_product, 'qty', 0)
        total = Decimal(
            getattr(cart_product.campaign_product, 'price', '0')) * qty
        items.append(f"{str(i).zfill(digits)}. " +
                     _('ITEM_INFO{name}{qty}{dollar_sign}{total}\n').format(
                         name=name,
                         qty=qty,
                         dollar_sign=cart_product.campaign_product.currency_sign,
                         total=total
                     )
                     )
        subtotal += total
    return items, subtotal


def i18n_get_comment_command_order(comment: CampaignComment):
    try:
        order: Order = Order.objects.filter(campaign=comment.campaign,
                                            customer_id=comment.customer_id).latest('created_at')
    except Order.DoesNotExist:
        return _('COMMENT_COMMAND_ORDER_NO_ORDER')

    # TODO: codes below in function is WIP since the Order model is not finalized atm

    text = [_('COMMENT_COMMAND_ORDER_MESSAGE_HEADER'), '\n-----\n']
    text.extend(_i18n_get_order_items(order))
    text.append(_('DELIVERY{dollar_sign}{delivery}\n'
                  ).format(dollar_sign=order.currency_sign,
                           delivery=order.checkout_details.get('delivery', 0)))
    text.append(_('OPTION{dollar_sign}{option}\n'
                  ).format(dollar_sign=order.currency_sign,
                           option=order.checkout_details.get('option', 0)))
    text.append(_('TOTAL{dollar_sign}{total}\n'
                  ).format(dollar_sign=order.currency_sign,
                           total=getattr(order, 'total', 0)))
    text.append(_('DETAIL{link}'
                  ).format(link=settings.SHOPPING_CART_URL))

    return ''.join(text)


def _i18n_get_order_items(order: Order):
    return [
        _('ITEM_INFO{name}{qty}{dollar_sign}{total}\n').format(
            name=getattr(product, 'name', ''),
            qty=getattr(product, 'qty', 0),
            dollar_sign=order.currency_sign,
            total=getattr(product, 'total', 0)
        )
        for product in order.products
    ]
