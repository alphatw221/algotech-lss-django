from decimal import Decimal

import database


from ._i18n import lang_translate_default_en
from backend.utils.text_processing.command_processor import Command
from django.conf import settings
from django.utils.translation import ugettext as _
# from backend.pymongo.mongodb import db


def get_comment_command_response(campaign, comment, command: Command, lang='en'):
    if command == Command.CART:
        return get_comment_command_cart(campaign, comment)
    # if command == Command.ORDER:
    #     return i18n_get_comment_command_order(campaign, comment)
    return ''


def get_comment_command_cart(campaign, comment):
    try:
        pre_order = database.lss.pre_order.PreOrder.get_object(customer_id=comment['customer_id'], campaign_id= campaign['id'], platform= comment['platform'])
    except Exception as e:
        return _('COMMENT_COMMAND_CART_NO_CART_PRODUCT')

    if not pre_order:
        return _('COMMENT_COMMAND_CART_NO_CART_PRODUCT')
    if not pre_order.data.get('products'):
        return _('COMMENT_COMMAND_CART_NO_CART_PRODUCT')
    order_products = database.lss.order_product.OrderProduct.filter(pre_order_id=pre_order.id)

    items = get_order_items(order_products)

    text = [_('COMMENT_COMMAND_CART_MESSAGE_HEADER'), '\n-----\n']
    text.extend(items)
    text.append('-----\n')
    text.append(_('TOTAL{dollar_sign}{total}\n'
                  ).format(total="{:.2f}".format(pre_order['subtotal']), dollar_sign=campaign["currency_sign"]))
    text.append(_('DETAIL{link}\n'
                  ).format(link=settings.SHOPPING_CART_URL + '/' + str(pre_order['_id'])))

    return ''.join(text)


# def _i18n_get_cart_products(campaign_product_dict, order_products):
#     items = []
#     count = len(order_products)
#     digits = 2 if count < 100 else len(str(count))
#     for i, order_product in enumerate(order_products, 1):
#         campaign_product=campaign_product_dict[order_product['campaign_product_id']]
#         name = getattr(campaign_product, 'name', '')
#         qty = getattr(order_product, 'qty', 0)
#         total = Decimal(
#             getattr(campaign_product, 'price', '0')) * qty
#         items.append(
#             f"{str(i).zfill(digits)}. " +
#             _('ITEM_INFO{name}{qty}{dollar_sign}{total}\n').format(
#                 name=name,
#                 qty=qty,
#                 dollar_sign=campaign_product['currency_sign'],
#                 total="{:.2f}".format(total)
#             )
#         )
#         if (i < count):
#             items.append('\n')
#     return items


# def i18n_get_comment_command_order(campaign, comment):
#     try:
#         order = database.lss.order.Order.get_object(campaign_id = campaign['id'], customer_id = comment['customer_id'])
#         order = db.api_order.find_one({"$query": {
#                                       "campaign_id": campaign['id'], "customer_id": comment['customer_id']}, "$orderby": {"created_at": -1}})
#     except Exception:
#         return _('COMMENT_COMMAND_ORDER_NO_ORDER')

#     if not order:
#         return _('COMMENT_COMMAND_ORDER_NO_ORDER')

#     order_products = db.api_order_product.find({"order_id": order['id']})

#     if not order_products:
#         return _('COMMENT_COMMAND_ORDER_NO_ORDER')

#     text = [_('COMMENT_COMMAND_ORDER_MESSAGE_HEADER'), '\n-----\n']

#     items = _i18n_get_order_items(order_products)
#     text.extend(items)
#     text.append(_('DELIVERY{dollar_sign}{delivery}\n'
#                   ).format(dollar_sign=campaign["currency_sign"],
#                            delivery=order["checkout_details"].get('delivery', 0)))
#     text.append(_('OPTION{dollar_sign}{option}\n'
#                   ).format(dollar_sign=campaign["currency_sign"],
#                            option=order["checkout_details"].get('option', 0)))
#     text.append(_('TOTAL{dollar_sign}{total}\n'
#                   ).format(dollar_sign=campaign["currency_sign"],
#                            total=order.get('total', 0)))
#     text.append(_('DETAIL{link}'
#                   ).format(link=settings.SHOPPING_CART_URL))

#     return ''.join(text)


def get_order_items(order_products):

    items = []
    count = order_products.count()
    digits = 2 if count < 100 else len(str(count))
    for i, order_product in enumerate(order_products, 1):
        name = order_product.get('name', '')
        qty = order_product.get('qty', 0)
        total = Decimal(
            order_product.get('price', 0)) * qty
        items.append(
            f"{str(i).zfill(digits)}. " +
            _('ITEM_INFO{name}{qty}{dollar_sign}{total}\n').format(
                name=name,
                qty=qty,
                dollar_sign=order_product.get('currency_sign', "$"),
                total="{:.2f}".format(total)
            )
        )
        if (i < count):
            items.append('\n')
    return items
