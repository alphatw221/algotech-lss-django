
from django.conf import settings

from ._hitpay_caller import HitPayApiCaller


def create_payment(api_key, email, amount, currency, reference_number, redirect_url, webhook_url):
    try:
        headers = {
                'X-BUSINESS-API-KEY': api_key,
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            }
        params = {
            'email': email,
            'name': 'name',
            'redirect_url': redirect_url,
            'webhook': webhook_url,
            'amount': amount,
            'currency': currency,
            'reference_number': reference_number,
        }
            
        return HitPayApiCaller('v1/payment-requests',headers=headers,params=params).post()
    except Exception:
        return False,None