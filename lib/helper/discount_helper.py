import traceback
from api import models
import database
import lib
import math
from datetime import datetime, timedelta

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
                cart = kwargs['cart']
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




class PointDiscountProcessor:

    def __init__(self, api_user, user_subscription, buyer_wallet, meta_point, points_used) -> None:
        self.api_user = api_user
        self.user_subscription = user_subscription
        self.buyer_wallet = buyer_wallet
        self.meta_point = meta_point
        self.points_used = points_used
        self.points_earned = 0

    def compute_point_discount(self):
        return math.floor( (self.points_used/self.meta_point.get('redemption_rate_point',1)))*self.meta_point.get('redemption_rate_cash',0)
        
    

    def compute_points_earned(self, subtotal_after_discount=0):
        
        point_redemption_rate = self.meta_point.get('default_point_redemption_rate',0)
        for tier in self.meta_point.get('reward_table',[]):
            if subtotal_after_discount < tier.get('upper_bound',0):
                point_redemption_rate = tier.get('point_redemption_rate',0)
                break
        self.points_earned = math.floor(subtotal_after_discount * point_redemption_rate)
        return self.points_earned

    def compute_expired_date(self):
        point_validity = self.meta_point.get('point_validity',None)
        if not point_validity:
            return None
        return datetime.utcnow()+timedelta(days=30*point_validity)


    def update_wallet(self):
        if not self.api_user:
            return

        if self.points_earned <= 0:
            return 

        if not self.buyer_wallet:
            if models.user.buyer_wallet.BuyerWallet.objects.filter(buyer = self.api_user, user_subscription=self.user_subscription).exists():
                self.buyer_wallet = models.user.buyer_wallet.BuyerWallet.objects.get(buyer = self.api_user, user_subscription=self.user_subscription)
            else:
                self.buyer_wallet = models.user.buyer_wallet.BuyerWallet.objects.create(buyer = self.api_user, user_subscription=self.user_subscription)

        self.buyer_wallet.points-=self.points_used if self.points_used else 0
        self.buyer_wallet.points+=self.points_earned if self.points_earned else 0
        self.buyer_wallet.save()

    

class SHCPointDiscountProcessor(PointDiscountProcessor):
    pass
   

point_discount_processor_map = {"617":SHCPointDiscountProcessor}
def get_point_discount_processor_class(user_subscription):
    return point_discount_processor_map.get(str(user_subscription.id),PointDiscountProcessor)