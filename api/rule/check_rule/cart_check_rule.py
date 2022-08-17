from django.conf import settings
from datetime import datetime
from api.utils.error_handle.error.cart_error import CartErrors
from api import models


class CartCheckRule():

    @staticmethod
    def is_campaign_product_exist(**kwargs):
        cart = kwargs.get('cart')
        campaign_product = kwargs.get('campaign_product')
        campaign_product_id = kwargs.get('campaign_product_id')
        if not campaign_product:
            if campaign_product_id in cart.products:
                del cart.products[campaign_product_id]
                cart.save()
            raise CartErrors.CartException('helper.campaign_product_been_deleted')
    
    @staticmethod
    def is_cart_lock(**kwargs):
        api_user = kwargs.get('api_user')
        cart = kwargs.get('cart')
        if not api_user:
            return
        if api_user.type == 'customer':
            return
        if cart.lock_at and datetime.timestamp(cart.lock_at)+settings.CART_LOCK_INTERVAL > datetime.timestamp(datetime.now()):
            raise CartErrors.CartException('helper.cart_in_use')

    @staticmethod
    def is_qty_valid(**kwargs):
        qty = kwargs.get('qty')
        if type(qty) != int or qty <=0:
            raise CartErrors.CartException('helper.qty_invalid')

    @staticmethod
    def is_stock_avaliable(**kwargs):
        campaign_product = kwargs.get('campaign_product')
        cart = kwargs.get('cart')
        request_qty = kwargs.get('qty')

        original_qty = cart.products[campaign_product.id].get('qty',0)
        qty_difference = int(request_qty)-original_qty
        if qty_difference and campaign_product.qty_for_sale-campaign_product.qty_sold < qty_difference:
            raise CartErrors.UnderStock("helper.out_of_stock")
        return {"qty_difference" : qty_difference}

    @staticmethod
    def is_campaign_product_removeable(**kwargs):

        api_user = kwargs.get('api_user')
        campaign_product = kwargs.get('campaign_product')

        if not api_user or not campaign_product:
            return
        if api_user.type=="user":
            return
        if not campaign_product.customer_removable:
            raise CartErrors.RemoveNotAllowed("helper.not_removable")

    @staticmethod
    def is_campaign_product_editable(**kwargs):


        api_user = kwargs.get('api_user')
        campaign_product = kwargs.get('campaign_product')

        if not api_user or not campaign_product:
            return
        if api_user.type=="user":
            return
        if not campaign_product.customer_editable:
            raise CartErrors.EditNotAllowed("helper.not_editable")
        if campaign_product.type == models.campaign.campaign_product.TYPE_LUCKY_DRAW:
            raise CartErrors.EditNotAllowed("helper.not_editable")



    @staticmethod
    def is_under_max_limit(**kwargs):

        campaign_product = kwargs.get('campaign_product')
        qty = kwargs.get('qty')

        if not campaign_product or not qty:
            return

        if campaign_product.max_order_amount and qty > campaign_product.max_order_amount:
            raise CartErrors.CartException(
                "helper.exceeds_max_order_amount")

    @staticmethod
    def is_cart_empty(**kwargs):

        cart = kwargs.get('api_cart')

        if not bool(cart['products']):
            raise CartErrors.CartException('helper.cart_is_empty')

    @staticmethod
    def allow_checkout(**kwargs):

        api_user = kwargs.get('api_user')
        campaign = kwargs.get('campaign')
        if api_user and api_user.type=="user":
            return
        if campaign.stop_checkout:
        # if not campaign.meta.get('allow_checkout', True):
            raise CartErrors.CartException('helper.unable_purchase_now')


    # @staticmethod
    # def campaign_product_type(**kwargs):

    #     campaign_product = kwargs.get('campaign_product')

    #     if campaign_product.type == models.campaign.campaign_product.TYPE_LUCKY_DRAW :
    #         api_campaign_product['price'] = 0
    #     elif api_campaign_product['type'] == 'n/a':
    #         raise CartErrors.UnderStock('out of stock')
    