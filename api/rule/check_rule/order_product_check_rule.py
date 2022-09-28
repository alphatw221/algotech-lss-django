from django.conf import settings
from datetime import datetime
import lib


class OrderProductCheckRule:

    # @staticmethod
    # def is_stock_avaliable(**kwargs):


    #     campaign_product = kwargs.get('campaign_product')
    #     order_product = kwargs.get('order_product')

    #     qty_for_sale = campaign_product.data.get('qty_for_sale')
    #     qty_add_to_cart = campaign_product.data.get('qty_add_to_cart')
    #     qty_pending_payment = campaign_product.data.get('qty_pending_payment')
    #     qty_sold = campaign_product.data.get('qty_sold')

    #     stock_qty = qty_for_sale - qty_sold 

    #     if not stock_qty :
    #         raise lib.error_handle.error.pre_order_error.PreOrderErrors.UnderStock('helper.out_of_stock')
        
    #     original_order_product_qty = order_product.data.get('qty')
    #     order_product_qty = stock_qty if original_order_product_qty > stock_qty else original_order_product_qty

    #     qty_difference = order_product_qty - original_order_product_qty
        
    #     return {'qty':order_product_qty, "qty_difference" : qty_difference}

    @staticmethod
    def is_stock_avaliable_for_checkout(**kwargs):


        campaign_product = kwargs.get('campaign_product')
        order_product = kwargs.get('order_product')

        original_order_product_qty = order_product.data.get('qty')

        qty_for_sale = campaign_product.data.get('qty_for_sale')
        qty_pending_payment = campaign_product.data.get('qty_pending_payment')
        qty_sold = campaign_product.data.get('qty_sold')

        if campaign_product.data.get('oversell'):
            return {'qty':original_order_product_qty }

        stock_qty = qty_for_sale - qty_sold - qty_pending_payment

        if not stock_qty :
            raise lib.error_handle.error.pre_order_error.PreOrderErrors.UnderStock('helper.out_of_stock')
        
        original_order_product_qty = order_product.data.get('qty')
        order_product_qty = stock_qty if original_order_product_qty > stock_qty else original_order_product_qty
        qty_difference = order_product_qty - original_order_product_qty
        
        return {'qty':order_product_qty, "qty_difference" : qty_difference}