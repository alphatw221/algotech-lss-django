
from api.utils.error_handle.error.api_error import ApiVerifyError

from datetime import datetime
class StripeCheckRule():

    @staticmethod
    def is_payment_successed(**kwargs):
        paymentIntent = kwargs.get('paymentIntent')

        if paymentIntent.status != "succeeded":
            raise ApiVerifyError('payment not succeeded')


    @staticmethod
    def is_period_valid(**kwargs):

        subscription_plan = kwargs.get('subscription_plan')
        period = kwargs.get('period')

        amount = subscription_plan.get('price',{}).get(period)

        if not amount :
            raise ApiVerifyError('invalid period')
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

        if int(amount*100) != paymentIntent.amount:
            raise ApiVerifyError('payment amount error')


    def adjust_price_if_promo_code_valid(**kwargs):

        promoCode = kwargs.get('promoCode')
        country_plan = kwargs.get('country_plan')
        amount = kwargs.get('amount')

        if promoCode and promoCode == country_plan.promo_code:
            amount = amount*country_plan.promo_discount_rate
            return {'amount':amount}

    def is_upgrade_plan_valid(**kwargs):

        upgrade_avaliable_dict={
            'trial':['lite','standard','premium'],
            'lite':['lite','standard','premium'],
            'standard':['standard','premium'],
            'premium':['premium']
        }

        api_user_subscription = kwargs.get('api_user_subscription')
        plan = kwargs.get('plan')

        upgrade_avaliable_list=upgrade_avaliable_dict.get(api_user_subscription.type)

        if plan not in upgrade_avaliable_list:
            raise ApiVerifyError('not valid upgrade plan')

    def adjust_amount_if_subscription_undue(**kwargs):

        amount = kwargs.get('amount')

        api_user_subscription = kwargs.get('api_user_subscription')

        if datetime.timestamp(datetime.now())>datetime.timestamp(api_user_subscription.expired_at):
            return {'adjust_amount':0.0}

        expired_date = api_user_subscription.expired_at.date()
        started_date = api_user_subscription.started_at.date()

        adjust_amount = int(api_user_subscription.purchase_price*((expired_date-datetime.now().date()).days/(expired_date-started_date).days))
        return {'amount':amount-adjust_amount,'adjust_amount':adjust_amount}


        