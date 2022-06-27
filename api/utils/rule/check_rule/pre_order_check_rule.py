from django.conf import settings
from datetime import datetime
from api.utils.error_handle.error.pre_order_error import PreOrderErrors
from api.utils.common.verify import Verify


class PreOrderCheckRule():

    @staticmethod
    def is_campaign_product_exist(**kwargs):
        api_campaign_product = kwargs.get('api_campaign_product')
        if not api_campaign_product:
            raise PreOrderErrors.PreOrderException('campaign product has already been deleted')

    @staticmethod
    def is_order_lock(**kwargs):
        api_user = kwargs.get('api_user')
        api_pre_order = kwargs.get('api_pre_order')
        if not api_user:
            return
        if api_user.type == 'customer':
            return
        if api_pre_order['lock_at'] and datetime.timestamp(api_pre_order['lock_at'])+settings.CART_LOCK_INTERVAL > datetime.timestamp(datetime.now()):
            raise PreOrderErrors.PreOrderException('Cart in use')

    @staticmethod
    def is_qty_valid(**kwargs):
        qty = kwargs.get('qty')
        if not qty:
            raise PreOrderErrors.PreOrderException('please enter qty')
        qty = int(qty)
        if not qty:
            raise PreOrderErrors.PreOrderException(
                'qty can not be zero or negitive')
        return {'qty': qty}

    @staticmethod
    def is_stock_avaliable(**kwargs):
        api_campaign_product = kwargs.get('api_campaign_product')
        request_qty = kwargs.get('qty')
        api_order_product = kwargs.get('api_order_product')
        original_qty = api_order_product['qty'] if api_order_product else 0
        qty_difference = int(request_qty)-original_qty
        if qty_difference and api_campaign_product["qty_for_sale"]-api_campaign_product["qty_sold"] < qty_difference:
            raise PreOrderErrors.UnderStock("out of stock")
        return {"qty_difference" : qty_difference}

    @staticmethod
    def is_order_product_removeable(**kwargs):

        api_user = kwargs.get('api_user')
        api_campaign_product = kwargs.get('api_campaign_product')

        if not api_user or not api_campaign_product:
            return
        if api_user.type=="user":
            return
        if not api_campaign_product['customer_removable']:
            raise PreOrderErrors.RemoveNotAllowed("not removable")

    @staticmethod
    def is_order_product_editable(**kwargs):


        api_user = kwargs.get('api_user')
        api_campaign_product = kwargs.get('api_campaign_product')

        if not api_user or not api_campaign_product:
            return
        if api_user.type=="user":
            return
        if not api_campaign_product.get('customer_editable',False):
            raise PreOrderErrors.EditNotAllowed("not editable")
        if api_campaign_product.get('type') == "lucky_draw":
            raise PreOrderErrors.EditNotAllowed("not editable")


    @staticmethod
    def is_order_product_addable(**kwargs):

        api_pre_order = kwargs.get('api_pre_order')
        api_campaign_product = kwargs.get('api_campaign_product')
        if str(api_campaign_product["id"]) in api_pre_order["products"]:
            raise PreOrderErrors.PreOrderException(
                "product already in pre_order")

    @staticmethod
    def is_under_max_limit(**kwargs):

        api_campaign_product = kwargs.get('api_campaign_product')
        qty = kwargs.get('qty')
        lucky_draw_repeat = kwargs.get('lucky_draw_repeat')
        if not api_campaign_product or not qty:
            return
        if lucky_draw_repeat:
            return
        if api_campaign_product.get('max_order_amount') and qty > api_campaign_product.get('max_order_amount'):
            raise PreOrderErrors.PreOrderException(
                "Product quantity exceeds max order amount.")

    @staticmethod
    def is_order_empty(**kwargs):

        api_pre_order = kwargs.get('api_pre_order')

        if not bool(api_pre_order['products']):
            raise PreOrderErrors.PreOrderException('cart is empty')

    @staticmethod
    def allow_checkout(**kwargs):

        api_user = kwargs.get('api_user')
        pre_order = kwargs.get('pre_order')
        if not pre_order:       #temp only
            campaign = kwargs.get('campaign')
            if api_user and api_user.type=="user":
                return
            if not campaign.data.get('meta',{}).get('allow_checkout', True):
                raise PreOrderErrors.PreOrderException('Sorry, you are unable to make that purchase right now.')

        else:
            campaign = pre_order.campaign

            if api_user and api_user.type=="user":
                return
            if not campaign.meta.get('allow_checkout', 1):
                raise PreOrderErrors.PreOrderException('Sorry, you are unable to make that purchase right now.')

    @staticmethod
    def campaign_product_type(**kwargs):

        api_campaign_product = kwargs.get('api_campaign_product')

        if api_campaign_product['type'] == 'lucky_draw' or api_campaign_product['type'] == 'lucky_draw-fast':
            api_campaign_product['price'] = 0
        elif api_campaign_product['type'] == 'n/a':
            raise PreOrderErrors.UnderStock('out of stock')
    
    @staticmethod
    def orders_limit(**kwargs):
        api_user = kwargs.get('api_user')
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)