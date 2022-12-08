
from api.models.user.promotion_code import PromotionCode

from lib.error_handle.error.api_error import ApiVerifyError
from datetime import datetime

from business_policy.marketing_plan import MarketingPlan
import lib
class StripeCheckRule():

    @staticmethod
    def is_payment_successed(**kwargs):
        paymentIntent = kwargs.get('paymentIntent')

        if paymentIntent.status != "succeeded":
            raise ApiVerifyError('helper.payment_not_succeeded')


    @staticmethod
    def is_period_valid(**kwargs):

        subscription_plan = kwargs.get('subscription_plan')
        period = kwargs.get('period')
        
        amount = subscription_plan.get('price',{}).get(period)
        if not amount :
            raise ApiVerifyError('helper.invalid_period')
        return {'amount':amount}

    @staticmethod
    def is_promo_code_valid(**kwargs):

        promoCode = kwargs.get('promoCode')
        country_plan = kwargs.get('country_plan')

        if promoCode and promoCode != country_plan.promo_code:
            raise ApiVerifyError('invalid promo code')

    def does_amount_match(**kwargs):

        amount = kwargs.get('amount')
        paymentIntent = kwargs.get('paymentIntent')
        if not paymentIntent:
            return
        if int(amount*100) != paymentIntent.amount:
            raise ApiVerifyError('helper.payment_amount_error')


    def adjust_price_if_promo_code_valid(**kwargs):

        promoCode = kwargs.get('promoCode')
        country_plan = kwargs.get('country_plan')
        amount = kwargs.get('amount')

        if promoCode and promoCode == country_plan.promo_code:
            amount = amount*country_plan.promo_discount_rate
            return {'amount':amount}
        
    def adjust_price_if_marketing_plan(**kwargs):
        amount = kwargs.get('amount')
        plans_detail = MarketingPlan.get_plans("current_plans")
        for key, val in plans_detail.items():
            if not val['expire_time']:
                if val['discount_rate']:
                    amount = amount * val['discount_rate']
        return {'amount':amount, 'marketing_plans':plans_detail}
    
    @staticmethod
    def adjust_price_if_welcome_gift_not_used(**kwargs):
        amount1 = kwargs.get('amount')
        marketing_plans = kwargs.get('marketing_plans', {})
        api_user = kwargs.get('api_user')
        amount2 = lib.util.marking_tool.WelcomeGiftUsedMark.check_mark(api_user, amount1)
        if amount1 != amount2:
            marketing_plans['welcome_gift'] =  MarketingPlan.welcome_gift()
        return {"amount": amount2, "marketing_plans": marketing_plans}
    def is_upgrade_plan_valid(**kwargs):

        upgrade_avaliable_dict={
            'trial':['lite','standard','premium'],
            'lite':['lite','standard','premium'],
            'standard':['standard','premium'],
            'premium':['premium'],
            'dealer':[]
        }

        api_user_subscription = kwargs.get('api_user_subscription')
        plan = kwargs.get('plan')

        upgrade_avaliable_list=upgrade_avaliable_dict.get(api_user_subscription.type)

        if plan not in upgrade_avaliable_list:
            raise ApiVerifyError('helper.not_valid_upgrade_plan')

    def adjust_amount_if_subscription_undue(**kwargs):

        amount = kwargs.get('amount')
        # print(amount)
        api_user_subscription = kwargs.get('api_user_subscription')

        if datetime.timestamp(datetime.now())>datetime.timestamp(api_user_subscription.expired_at):
            return {'adjust_amount':0.0}

        expired_date = api_user_subscription.expired_at.date()
        started_date = api_user_subscription.started_at.date()
        # print(api_user_subscription.purchase_price)
        adjust_amount = int(api_user_subscription.purchase_price*((expired_date-datetime.now().date()).days/(expired_date-started_date).days))
        # print(f'{adjust_amount} = int({api_user_subscription.purchase_price}*{(expired_date-datetime.now().date()).days})/{(expired_date-started_date).days}')
        return {'amount':amount-adjust_amount,'adjust_amount':adjust_amount}


        