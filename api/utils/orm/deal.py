from datetime import datetime
from api import models


def record_subscription_for_paid_user(user_subscription, purchased_plan, total, payer, original_plan=None):
    return models.user.deal.Deal.objects.create(
        user_subscription=user_subscription,
        original_plan=original_plan,
        purchased_plan=purchased_plan, 
        total=total, 
        status="success", 
        payer=payer, 
        payment_time=datetime.utcnow()
    )
    
def record_subscription_for_trial_user(user_subscription, api_user, original_plan=None):
    return models.user.deal.Deal.objects.create(
        user_subscription=user_subscription,
        original_plan=original_plan,
        purchased_plan='trial', 
        total=0, 
        payer=api_user, 
        payment_time=datetime.utcnow()
    )