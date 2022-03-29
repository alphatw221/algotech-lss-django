from django.conf import settings
from datetime import datetime
from api.utils.error_handle.error.pre_order_error import PreOrderErrors


class PreOrderCheckRule():

    @staticmethod
    def is_order_lock(**kwargs):
        api_user = kwargs.get('api_user')
        api_pre_order = kwargs.get('api_pre_order')
        if not api_user:
            return
        if api_user.type == 'customer':
            return
        if api_pre_order['lock_at'] and datetime.timestamp(api_pre_order['lock_at'])+settings.CART_LOCK_INTERVAL > datetime.timestamp(datetime.now()):
            raise PreOrderErrors.PreOrderException('cart in use')

    @staticmethod
    def is_qty_valid(**kwargs):
        qty = kwargs.get('qty')
        if not qty:
            raise PreOrderErrors.PreOrderException('please enter qty')
        qty = int(qty)
        if not qty:
            raise PreOrderErrors.PreOrderException(
                'qty can not be zero or negitive')
        return qty

    @staticmethod
    def is_stock_avaliable(**kwargs):
        api_campaign_product = kwargs.get('api_campaign_product')
        request_qty = kwargs.get('api_campaign_product')
        original_qty = kwargs.get('api_campaign_product')
        qty_difference = int(request_qty)-original_qty
        if qty_difference and api_campaign_product["qty_for_sale"]-api_campaign_product["qty_sold"] < qty_difference:
            raise PreOrderErrors.UnderStock("out of stock")
        return qty_difference

    @staticmethod
    def is_order_product_removeable(**kwargs):

        api_user = kwargs.get('api_user')
        api_campaign_product = kwargs.get('api_campaign_product')

        if not api_user:
            return
        if api_user.type=="user":
            return
        if not api_campaign_product['customer_removable']:
            raise PreOrderErrors.RemoveNotAllowed("not removable")

    @staticmethod
    def is_order_product_editable(**kwargs):


        api_user = kwargs.get('api_user')
        api_campaign_product = kwargs.get('api_campaign_product')

        if not api_user:
            return
        if api_user.type=="user":
            return
        if not api_campaign_product.get('customer_editable',False):
            raise PreOrderErrors.EditNotAllowed("not editable")


    @staticmethod
    def is_order_product_addable(**kwargs):

        api_pre_order = kwargs.get('api_pre_order')
        api_campaign_product = kwargs.get('api_campaign_product')

        if str(api_campaign_product["id"]) in api_pre_order["products"]:
            raise PreOrderErrors.PreOrderException(
                "product already in pre_order")

    @staticmethod
    def is_order_empty(**kwargs):

        api_pre_order = kwargs.get('api_pre_order')

        if not bool(api_pre_order['products']):
            raise PreOrderErrors.PreOrderException('cart is empty')

    @staticmethod
    def allow_checkout(**kwargs):

        api_user = kwargs.get('api_user')
        campaign = kwargs.get('campaign')

        if api_user and api_user.type=="user":
            return
        if not campaign.meta.get('allow_checkout', 1):
            raise PreOrderErrors.PreOrderException('check out not allow')

    @staticmethod
    def campaign_product_type(**kwargs):

        api_campaign_product = kwargs.get('api_campaign_product')

        if api_campaign_product['type'] == 'lucky_draw' or api_campaign_product['type'] == 'lucky_draw-fast':
            api_campaign_product['price'] = 0
        elif api_campaign_product['type'] == 'n/a':
            raise PreOrderErrors.UnderStock('out of stock')