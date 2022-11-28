from django.conf import settings
from datetime import datetime
from api import models
from api.models import campaign
import lib
import database

class CartCheckRule():


    @staticmethod
    def is_cart_lock(**kwargs):
        api_user = kwargs.get('api_user')
        cart = kwargs.get('cart')
        if not api_user:
            return
        if api_user.type == 'customer':
            return
        if cart.lock_at and datetime.timestamp(cart.lock_at)+settings.CART_LOCK_INTERVAL > datetime.timestamp(datetime.now()):
            raise lib.error_handle.error.cart_error.CartErrors.CartException('helper.cart_in_use')

    @staticmethod
    def is_qty_valid(**kwargs):
        qty = kwargs.get('qty')
        try:
            qty = int(qty)
            if  qty <0:
                raise lib.error_handle.error.cart_error.CartErrors.CartException('helper.qty_invalid')
            return {'qty':qty}
        except Exception:
            raise lib.error_handle.error.cart_error.CartErrors.CartException('helper.qty_invalid')
    

    # @staticmethod
    # def is_stock_avaliable(**kwargs):



    #     try:
    #         with database.lss.util.start_session() as session:
    #             with session.start_transaction():
                    




    #     except Exception:
    #         if attempts > 0:
    #             cls.__get_incremented_field(attempts=attempts-1)
    #         else:
    #             raise



    #     campaign_product = kwargs.get('campaign_product')
    #     campaign_product_data = kwargs.get('campaign_product_data')
    #     qty_difference = kwargs.get('qty_difference')


    #     if not qty_difference:
    #         return 

    #     if not campaign_product_data:
    #         campaign_product_data = campaign_product.__dict__

    #     able_to_add_to_cart = True
    #     if campaign_product_data.get('overbook'):
    #         able_to_add_to_cart = (campaign_product_data["qty_for_sale"]-campaign_product_data['qty_sold'] >= qty_difference) or campaign_product_data.get('oversell')
    #     else:
    #         able_to_add_to_cart = (campaign_product_data["qty_for_sale"]-campaign_product_data['qty_sold']-campaign_product_data['qty_add_to_cart'] >= qty_difference) or campaign_product_data.get('oversell')

    #     able_to_purchase = True
    #     if campaign_product_data.get('oversell'):
    #         pass    #do nothing
    #     else:
    #         able_to_purchase = campaign_product_data["qty_for_sale"]-campaign_product_data['qty_sold'] >= qty_difference

    #     if not able_to_add_to_cart or not able_to_purchase:
    #         raise lib.error_handle.error.cart_error.CartErrors.UnderStock("out_of_stock")
        



    @staticmethod
    def is_campaign_product_removeable(**kwargs):

        api_user = kwargs.get('api_user')
        campaign_product = kwargs.get('campaign_product')
        qty = kwargs.get('qty')
        if qty > 0:
            return
        if not api_user or not campaign_product:
            return
        if api_user.type=="user":
            return
        if not campaign_product.customer_removable:
            raise lib.error_handle.error.cart_error.CartErrors.RemoveNotAllowed("not_removable")

    @staticmethod
    def is_campaign_product_editable(**kwargs):


        api_user = kwargs.get('api_user')
        campaign_product = kwargs.get('campaign_product')
        cart = kwargs.get('cart')

        if not api_user or not campaign_product:
            return
        if api_user.type=="user":
            return
        if not campaign_product.customer_editable and str(campaign_product.id) in cart.products:
            raise lib.error_handle.error.cart_error.CartErrors.EditNotAllowed("not_editable")
        if campaign_product.type == models.campaign.campaign_product.TYPE_LUCKY_DRAW:
            raise lib.error_handle.error.cart_error.CartErrors.EditNotAllowed("not_editable")



    @staticmethod
    def is_under_max_limit(**kwargs):

        campaign_product = kwargs.get('campaign_product')
        qty = kwargs.get('qty')

        if not campaign_product or not qty:
            return

        if campaign_product.max_order_amount and qty > campaign_product.max_order_amount:
            raise lib.error_handle.error.cart_error.CartErrors.CartException(
                "exceeds_max_order_amount")

    @staticmethod
    def is_cart_empty(**kwargs):

        cart = kwargs.get('cart')

        if not bool(cart.products):
            raise lib.error_handle.error.cart_error.CartErrors.CartException('helper.cart_is_empty')

    @staticmethod
    def allow_checkout(**kwargs):

        api_user = kwargs.get('api_user')
        campaign = kwargs.get('campaign')
        if api_user and api_user.type=="user":
            return
        if campaign.stop_checkout:
        # if not campaign.meta.get('allow_checkout', True):
            raise lib.error_handle.error.cart_error.CartErrors.CartException('helper.unable_purchase_now')

    @staticmethod
    def campaign_product_type(**kwargs):

        api_user = kwargs.get('api_user')
        campaign_product = kwargs.get('campaign_product')

        if campaign_product.type == models.campaign.campaign_product.TYPE_PRODUCT:
            return
        if api_user and api_user.type == models.user.user.TYPE_SELLER:
            return
        else :
            raise lib.error_handle.error.cart_error.CartErrors.CartException('product_type_invalid')
    

    @staticmethod
    def wallet_enough_points(**kwargs):

        user_subscription = kwargs.get('user_subscription')
        api_user = kwargs.get('api_user')
        points_used = kwargs.get('points_used')

        if points_used <=0 or not points_used:
            return

        if not api_user:
            raise lib.error_handle.error.cart_error.CartErrors.CartException('points_not_enough')
            
        if not models.user.buyer_wallet.BuyerWallet.objects.filter(user_subscription=user_subscription, buyer = api_user).exists():
            raise lib.error_handle.error.cart_error.CartErrors.CartException('points_not_enough')
        
        buyer_wallet = models.user.buyer_wallet.BuyerWallet.objects.get(user_subscription=user_subscription, buyer = api_user)

        if buyer_wallet.points<points_used:
            raise lib.error_handle.error.cart_error.CartErrors.CartException('points_not_enough')
            
        return {'buyer_wallet':buyer_wallet}
    


    @staticmethod
    def is_point_discount_enable(**kwargs):

        campaign = kwargs.get('campaign')
        points_used = kwargs.get('points_used')

        if points_used <=0 or not points_used:
            return

        if not campaign.meta_point.get('enable'):
            raise lib.error_handle.error.cart_error.CartErrors.CartException('point_discount_not_enable')
        

    # @staticmethod
    # def campaign_product_type(**kwargs):

    #     campaign_product = kwargs.get('campaign_product')

    #     if campaign_product.type == models.campaign.campaign_product.TYPE_LUCKY_DRAW :
    #         api_campaign_product['price'] = 0
    #     elif api_campaign_product['type'] == 'n/a':
    #         raise CartErrors.UnderStock('out of stock')
    