from dataclasses import dataclass
from backend.api._api_caller import RestApiJsonCaller
from django.conf import settings


class HitPay_Helper:

    @dataclass
    class HitPayApiCaller(RestApiJsonCaller):
        domain_url: str = settings.HITPAY_API_URL


class PaymentMeta:
    #country : SG PH IN ID MY TW CN

    direct_payment = {
            "multiple":True,
            "fields":[
                {"key":"bank_number", "name":"Name of Bank/Payment Mode", "type":"number", "r":0, "c":0},
                {"key":"account_name", "name":"Account Name", "type":"text", "r":0, "c":1},
                {"key":"account_number", "name":"Account Number", "type":"number", "r":0, "c":2},
                {"key":"other_note", "name":"Other Note (Press enter to add new line)", "type":"text", "r":1, "c":0},
                {"key":"require_record", "name":"Require Customer's Payment Record", "type":"checkbox", "r":1, "c":1},
                {"key":"image", "name":None, "type":"image_file", "r":2, "c":0}
            ],
            "tab": "Direct Payment",
            "request_url": "/user-subscription/direct_payment/"
        }

    hitpay = {
            "multiple":False,
            "fields":[
                {"key":"payment_title", "name":"Payment Button Title", "type":"text", "r":0, "c":0},
                {"key":"currency_code", "name":"Currency Code", "type":"select", "r":0, "c":1, "options":[{'SGD':'SGD'},{'AUD':'AUD'},{'NTD':'NTD'}]},
                {"key":"api_key", "name":"APIKey", "type":"secret", "r":1, "c":0},
                {"key":"salt", "name":"Salt", "type":"text", "r":2, "c":0}
            ],
            "tab": "HitPay",
            "request_url": "/user-subscription/hitpay/"
        }
    
    paypal = {
            "multiple":False,
            "fields":[
                {"key":"client_id", "name":"Client ID", "type":"text", "r":0, "c":0},
                {"key":"currency_code", "name":"Currency Code", "type":"select", "r":0, "c":1, "options":[{'SGD':'SGD'},{'AUD':'AUD'},{'NTD':'NTD'}]},
                {"key":"secret", "name":"Secret", "type":"secret", "r":1, "c":0},
            ],
            "tab":"PayPal",
            "request_url": "/user-subscription/paypal/"
        }

    stripe = {
            "multiple":False,
            "fields":[
                {"key":"secret_key", "type":"text", "name":"Secret Key", "r":0, "c":0},
                {"key":"currency_code", "type":"select", "name":"Currency Code", "r":0, "c":1, "options":[{'SGD':'SGD'},{'AUD':'AUD'},{'NTD':'NTD'}]},
            ],
            "tab":"Stripe",
            "request_url": "/user-subscription/stripe/"
        }

    pay_mongo = {
            "multiple":False,
            "fields":[
                {"key":"secret_key", "name":"Secret Key", "type":"text", "r":0, "c":0},
            ],
            "tab":"Pay Mongo",
            "request_url": "/user-subscription/pay_mongo/"
        }

    first_data = {
            "multiple":False,
            "fields":[
                {"key":"store_id", "name":"Store ID", "type":"number", "r":0, "c":0},
                {"key":"share_secret", "name":"Share Secret", "type":"secret", "r":0, "c":1},
                {"key":"currency_code", "name":"Currency Code", "type":"number", "r":1, "c":0},
                {"key":"time_zone", "name":"Time Zone", "type":"select", "r":1, "c":1, "options":[{'Asia/Singapore':'Asia/Singapore'}]}
            ],
            "tab":"First Data IPG (Credit Card)",
            "request_url": "/user-subscription/first_data/"
        }


    SG = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']
    
    if settings.GCP_API_LOADBALANCER_URL == "https://sb.liveshowseller.ph":
        PH = ['direct_payment','paypal']
    else:
        PH = ['direct_payment','hitpay', 'stripe', 'pay_mongo', 'first_data']

    IN = ['direct_payment','hitpay','paypal']

    MY = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    TW = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    CN = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    @classmethod
    def get_meta(cls,country_code='SG'):

        payment_support_list = getattr(cls,country_code)
        print(payment_support_list)
        meta = {}
        for payment in payment_support_list:
            meta[payment] = getattr(cls,payment)
        return meta