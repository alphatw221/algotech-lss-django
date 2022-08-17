from api import models

def make_discount(before_discount_amount, discount):
    try:
        type = discount['type']
        meta = discount['meta']
        if type==models.campaign.discount.TYPE_PERCENT_OFF:
            rate = meta[models.campaign.discount.TYPE_PERCENT_OFF]['discount_rate']
            after_discount_amount = before_discount_amount*rate
            return after_discount_amount, before_discount_amount-after_discount_amount
    except Exception:
        return before_discount_amount, 0