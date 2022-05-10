
from api.utils.error_handle.error.api_error import ApiVerifyError


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

        promoCode = kwargs.get('promoCode')
        country_plan = kwargs.get('country_plan')
        paymentIntent = kwargs.get('paymentIntent')
        amount = kwargs.get('amount')
        
        if promoCode :
            amount = amount*country_plan.promo_discount_rate

        if int(amount*100) != paymentIntent.amount:
            raise ApiVerifyError('payment amount error')

    def adjust_price_if_promo_code_valid(**kwargs):

        promoCode = kwargs.get('promoCode')
        country_plan = kwargs.get('country_plan')
        amount = kwargs.get('amount')

        if promoCode and promoCode == country_plan.promo_code:
            amount = amount*country_plan.promo_discount_rate
            return {'amount':amount}