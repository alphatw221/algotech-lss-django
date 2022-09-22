import traceback
from api import models
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

def check_limitation(limitation, pre_order):
    try:

        if limitation['key']==models.discount_code.discount_code.LIMITATION_SPECIFIC_CAMPAIGN:
            campaign_id = int(limitation['campaign_id'])
            if pre_order.campaign.id != campaign_id:
                return False
        elif limitation['key']==models.discount_code.discount_code.LIMITATION_PRODUCT_OVER_NUMBER:
            number = limitation['number']
            if len(pre_order.products) < number:
                return False
        elif limitation['key']==models.discount_code.discount_code.LIMITATION_SUBTOTAL_OVER_AMOUNT:
            amount = limitation['amount']
            if pre_order.subtotal < amount:
                return False
    except Exception:
        return False
    return True

def check_limitations(limitations, pre_order):
    try:
        for limitation in limitations:
            if not check_limitation(limitation, pre_order):
                return False
    except Exception:
        return False
    return True