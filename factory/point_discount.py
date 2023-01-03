from api import models
import math
from datetime import datetime, timedelta

class PointDiscountProcessor:

    def __init__(self, api_user, user_subscription, buyer_wallet, meta_point, points_used = 0, points_earned = 0) -> None:
        self.api_user = api_user
        self.user_subscription = user_subscription
        self.buyer_wallet = buyer_wallet
        self.meta_point = meta_point
        self.points_used = points_used
        self.points_earned = points_earned

        
    def compute_point_discount(self):
        
        if self.meta_point.get('enable')!=True:
            return 0

        return math.floor( (self.points_used/self.meta_point.get('redemption_rate_point',1)))*self.meta_point.get('redemption_rate_cash',0)
        
    

    def compute_points_earned(self, subtotal_after_discount=0):

        if self.meta_point.get('enable')!=True:
            return 0

        point_redemption_rate = self.meta_point.get('default_point_redemption_rate',0)
        for tier in self.meta_point.get('reward_table',[]):
            if subtotal_after_discount < tier.get('upper_bound',0):
                point_redemption_rate = tier.get('point_redemption_rate',0)
                break
  
        return math.floor(point_redemption_rate * subtotal_after_discount)  


    def compute_expired_date(self):

        if self.meta_point.get('enable')!=True:
            return None

        point_validity = self.meta_point.get('point_validity',None)
        if not point_validity:
            return None
        
        if not self.points_earned:
            return None

        return datetime.utcnow()+timedelta(days=30*point_validity)

    def create_point_transaction(self, order_id=None):
        data = {
            "user_subscription": self.user_subscription,
            "buyer": self.api_user,
            "order_id": order_id,
            "earned": self.points_earned,
            "used": self.points_used,
            "expired_at": self.compute_expired_date()
        }
        models.user.point_transaction.PointTransaction.objects.create(**data)
        
    def update_wallet(self):
        if not self.api_user:
            return

        if self.points_used<=0 and self.points_earned <= 0 :
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