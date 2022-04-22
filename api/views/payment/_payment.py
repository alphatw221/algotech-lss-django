from dataclasses import dataclass
from backend.api._api_caller import RestApiJsonCaller
from django.conf import settings


class HitPay_Helper:

    @dataclass
    class HitPayApiCaller(RestApiJsonCaller):
        domain_url: str = settings.HITPAY_API_URL


class PaymentMeta:
    #country : SG PH IN ID MY TW CN VN TH KH HK AU

    direct_payment = {
            "multiple":True,
            "fields":[
                {"key":"mode", "name":"Name of Bank/Payment Mode", "type":"text", "r":0, "c":0, "w":4},
                {"key":"name", "name":"Account Name", "type":"text", "r":0, "c":1, "w":4},
                {"key":"number", "name":"Account Number", "type":"text", "r":0, "c":2, "w":4},
                {"key":"note", "name":"Other Note (Press enter to add new line)", "type":"textarea", "r":1, "c":0, "w":6},
                {"key":"require_customer_return", "name":"Require Customer's Payment Record", "type":"checkbox", "r":1, "c":1, "w":6},
                {"key":"image", "name":None, "type":"file", "r":2, "c":0, "w":11}
            ],
            "tab": "Direct Payment",
            "request_url": "api/user-subscription/direct_payment/"
        }

    hitpay = {
            "multiple":False,
            "fields":[
                {"key":"button_title", "name":"Payment Button Title", "type":"text", "r":0, "c":0, "w":6},
                {"key":"currency", "name":"Currency Code", "type":"select", "r":0, "c":1, "options":['SGD','AUD','NTD'], "w":6},
                {"key":"api_key", "name":"API Key", "type":"password", "r":1, "c":0, "w":12},
                {"key":"salt", "name":"Salt", "type":"text", "r":2, "c":0, "w":12}
            ],
            "tab": "HitPay",
            "request_url": "api/user-subscription/hitpay/"
        }
    
    paypal = {
            "multiple":False,
            "fields":[
                {"key":"clientId", "name":"Client ID", "type":"text", "r":0, "c":0, "w":6},
                {"key":"currency", "name":"Currency Code", "type":"select", "r":0, "c":1, "w":6, "options":['SGD','AUD','NTD']},
                {"key":"secret", "name":"Secret", "type":"password", "r":1, "c":0, "w":12},
            ],
            "tab":"PayPal",
            "request_url": "api/user-subscription/paypal/"
        }

    stripe = {
            "multiple":False,
            "fields":[
                {"key":"secret", "type":"password", "name":"Secret Key", "r":0, "c":0, "w":6},
                {"key":"currency", "type":"select", "name":"Currency Code", "r":0, "c":1, "w":6, "options":[
                        'USD', 'AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD',
                        'BDT', 'BGN', 'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BSD', 'BWP', 'BYN', 'BZD', 'CAD', 'CDF',
                        'CHF', 'CLP', 'CNY', 'COP', 'CRC', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EGP', 'ETB',
                        'EUR', 'FJD', 'FKP', 'GBP', 'GEL', 'GIP', 'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK',
                        'HTG', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JMD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KRW',
                        'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'MAD', 'MDL', 'MGA', 'MKD', 'MMK', 'MNT',
                        'MOP', 'MRO', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR',
                        'NZD', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF',
                        'SAR', 'SBD', 'SCR', 'SEK', 'SGD', 'SHP', 'SLL', 'SOS', 'SRD', 'STD', 'SZL', 'THB', 'TJS',
                        'TOP', 'TRY', 'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'UYU', 'UZS', 'VND', 'VUV', 'WST', 'XAF',
                        'XCD', 'XOF', 'XPF', 'YER', 'ZAR', 'ZMW'
                    ]},
            ],
            "tab":"Stripe",
            "request_url": "api/user-subscription/stripe/"
        }

    pay_mongo = {
            "multiple":False,
            "fields":[
                {"key":"secret", "name":"Secret Key", "type":"password", "r":0, "c":0, "w":12},
            ],
            "tab":"Pay Mongo",
            "request_url": "api/user-subscription/pay_mongo/"
        }

    first_data = {
            "multiple":False,
            "fields":[
                {"key":"storeId", "name":"Store ID", "type":"text", "r":0, "c":0, "w":6},
                {"key":"sharedSecret", "name":"Share Secret", "type":"password", "r":0, "c":1, "w":6},
                {"key":"currency", "name":"Currency Code", "type":"select", "r":1, "c":0, "w":6, "options":['702', '703']},
                {"key":"timezone", "name":"Time Zone", "type":"select", "r":1, "c":1, "w":6, "options":['Asia/Singapore']}
            ],
            "tab":"First Data IPG (Credit Card)",
            "request_url": "api/user-subscription/first_data/"
        }


    SG = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']
    
    if settings.GCP_API_LOADBALANCER_URL == "https://sb.liveshowseller.ph":
        PH = ['direct_payment','paypal']
    else:
        PH = ['direct_payment','hitpay', 'stripe', 'pay_mongo', 'first_data']

    IN = ['direct_payment','hitpay','paypal']
    
    VN = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    MY = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    TW = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    CN = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    KH = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    AU = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    HK = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    @classmethod
    def get_meta(cls,country_code='SG'):

        payment_support_list = getattr(cls,country_code)
        
        meta = {}
        for payment in payment_support_list:
            meta[payment] = getattr(cls,payment)
        return meta