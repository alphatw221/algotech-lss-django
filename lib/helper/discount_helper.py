from api import models
import lib
def make_discount(before_discount_amount, discount_code):
    try:
        type = discount_code['type']
        meta = discount_code['meta']
        if type==models.discount_code.discount_code.TYPE_PERCENT_OFF:
            rate = meta[models.discount_code.discount_code.TYPE_PERCENT_OFF]['discount_rate']
            after_discount_amount = before_discount_amount*rate
            return after_discount_amount, before_discount_amount-after_discount_amount
        elif type==models.discount_code.discount_code.TYPE_DEDUCT:
            deduct_amount = meta[models.discount_code.discount_code.TYPE_DEDUCT]['deduct_amount']
            after_discount_amount = before_discount_amount-deduct_amount
            return after_discount_amount, deduct_amount


    except Exception:

        return before_discount_amount, 0
    return before_discount_amount, 0

def check_limitation(limitation, pre_order):
    try:

        if limitation['key']==models.discount_code.discount_code.LIMITATION_SPECIFIC_CAMPAIGN:
            campaign_id = limitation['campaign_id']
            if pre_order.campaign.id != campaign_id:
                return False
        elif limitation['key']==models.discount_code.discount_code.LIMITATION_SPECIFIC_CAMPAIGN:
            pass
        elif limitation['key']==models.discount_code.discount_code.LIMITATION_SUBTOTAL_OVER_AMOUNT:
            pass
    except Exception:
        return False
    return True