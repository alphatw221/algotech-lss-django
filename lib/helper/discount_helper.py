import traceback
from api import models
import database
import lib
def make_discount(before_discount_amount, discount_code):
    try:
        type = discount_code['type']
        discount_type = discount_code['discount_type']
        meta = discount_code['meta']
        if type ==models.discount_code.discount_code.TYPE_CART_REFERAL:
            pass
        else:
            pass

        if discount_type==models.discount_code.discount_code.DISCOUNT_TYPE_PERCENT_OFF:
            rate = meta['discount_rate']
            
            after_discount_amount = before_discount_amount*(1-rate/100)
            return after_discount_amount, before_discount_amount-after_discount_amount
        elif discount_type==models.discount_code.discount_code.DISCOUNT_TYPE_DEDUCT:
            deduct_amount = meta['deduct_amount']
            after_discount_amount = before_discount_amount-deduct_amount
            if after_discount_amount < 0:
                after_discount_amount = 0
            return after_discount_amount, before_discount_amount-after_discount_amount


    except Exception:
        print(traceback.format_exc())
        return before_discount_amount, 0
    return before_discount_amount, 0




def make_discount_for_pre_order(pre_order):
    try:
        discount_code = pre_order.applied_discount

        type = discount_code['type']
        discount_type = discount_code['discount_type']
        meta = discount_code['meta']

        if discount_type==models.discount_code.discount_code.DISCOUNT_TYPE_PERCENT_OFF:
            rate = meta['discount_rate']
            
            pre_order.discount = pre_order.subtotal * (rate/100)
            return

        elif discount_type==models.discount_code.discount_code.DISCOUNT_TYPE_DEDUCT:
            deduct_amount = meta['deduct_amount']

            pre_order.discount = deduct_amount
            return

    except Exception:
        pre_order.discount = 0
        pass


def check_limitation(limitation, **kwargs):
    try:

        if limitation['key']==models.discount_code.discount_code.LIMITATION_SPECIFIC_CAMPAIGN:
            campaign_id = int(limitation['campaign_id'])
            pre_order = kwargs['pre_order']
            if pre_order.campaign.id != campaign_id:
                return False
        elif limitation['key']==models.discount_code.discount_code.LIMITATION_PRODUCT_OVER_NUMBER:
            number = limitation['number']
            pre_order = kwargs['pre_order']
            if len(pre_order.products) < number:
                return False
        elif limitation['key']==models.discount_code.discount_code.LIMITATION_SUBTOTAL_OVER_AMOUNT:
            amount = limitation['amount']
            pre_order = kwargs['pre_order']
            if pre_order.subtotal < amount:
                return False
        elif limitation['key']==models.discount_code.discount_code.LIMITATION_DISCOUNT_CODE_USABLE_TIME:
            times = limitation['times']
            discount_code = kwargs['discount_code']
            if discount_code.used_count>=times:
                return False
    except Exception:
        return False
    return True

def check_limitations(limitations, **kwargs):
    try:
        for limitation in limitations:
            if not check_limitation(limitation, **kwargs):
                return False
    except Exception:
        return False
    return True

class CartDiscountHelper:

    @classmethod
    def make_discount(cls, cart):
        try:
            discount_code = cart.applied_discount

            type = discount_code['type']
            discount_type = discount_code['discount_type']
            meta = discount_code['meta']

            if discount_type==models.discount_code.discount_code.DISCOUNT_TYPE_PERCENT_OFF:
                rate = meta['discount_rate']
                
                cart.discount = cls.__caculate_subtotal(cart) * (rate/100)
                return

            elif discount_type==models.discount_code.discount_code.DISCOUNT_TYPE_DEDUCT:
                deduct_amount = meta['deduct_amount']

                cart.discount = deduct_amount
                return
        except Exception:
            print(traceback.format_exc())
            cart.discount = 0

    @classmethod
    def check_limitation(cls, limitation, **kwargs):
        try:

            if limitation['key']==models.discount_code.discount_code.LIMITATION_SPECIFIC_CAMPAIGN:
                campaign_id = int(limitation['campaign_id'])
                pre_order = kwargs['cart']
                if cart.campaign.id != campaign_id:
                    return False
            elif limitation['key']==models.discount_code.discount_code.LIMITATION_PRODUCT_OVER_NUMBER:
                number = limitation['number']
                cart = kwargs['cart']
                if len(cart.products) < number:
                    return False
            elif limitation['key']==models.discount_code.discount_code.LIMITATION_SUBTOTAL_OVER_AMOUNT:
                amount = limitation['amount']
                cart = kwargs['cart']
                cart_subtotal = cls.__caculate_subtotal(cart)
                if cart_subtotal < amount:
                    return False
            elif limitation['key']==models.discount_code.discount_code.LIMITATION_DISCOUNT_CODE_USABLE_TIME:
                times = limitation['times']
                discount_code = kwargs['discount_code']
                if discount_code.used_count>=times:
                    return False
        except Exception:
            return False
        return True

    

    @classmethod
    def check_limitations(cls, limitations, **kwargs):
        try:
            for limitation in limitations:
                if not check_limitation(limitation, **kwargs):
                    return False
        except Exception:
            return False
        return True
    

    @staticmethod
    def __caculate_subtotal(cart):

        cart.campaign
        campaign_product_dict = database.lss_cache.campaign_product.get_product_dict(cart.campaign.id, bypass=True)      #temp
        subtotal = 0
        for campaign_product_id_str, qty in cart.products.items():
            subtotal+=campaign_product_dict.get(campaign_product_id_str,{}).get('price',0)*qty
        return subtotal