from dataclasses import dataclass
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils import translation

class PaymentMeta():
    #country : SG PH IN ID MY TW CN VN TH KH HK AU
    @classmethod
    def direct_payment(cls):
        direct_payment = {
                "multiple":True,
                "fields":[
                    {"key":"mode", "name":_("PAYMENT/DIRECT_PAYMENT/NAME_OF_BANK_OR_PAYMENT_MODE"), "type":"text", "r":0, "c":0, "w":4},
                    {"key":"name", "name":_("PAYMENT/DIRECT_PAYMENT/ACCOUNT_NAME"), "type":"text", "r":0, "c":1, "w":4},
                    {"key":"number", "name":_("PAYMENT/DIRECT_PAYMENT/ACCOUNT_NUMBER"), "type":"text", "r":0, "c":2, "w":4},
                    {"key":"note", "name":_("PAYMENT/DIRECT_PAYMENT/OTHER_NOTE"), "type":"textarea", "r":1, "c":0, "w":6},
                    {"key":"require_customer_return", "name":_("PAYMENT/DIRECT_PAYMENT/REQUIRE_CUSTOMER_PAYMENT_RECORD"), "type":"checkbox", "r":1, "c":1, "w":6},
                    {"key":"image", "name":None, "type":"file", "r":2, "c":0, "w":11}
                ],
                "tab": "Direct Payment",
                "request_url": "api/user-subscription/direct_payment/"
            }
        return direct_payment
    
    @classmethod
    def hitpay(cls):
        hitpay = {
            "multiple":False,
            "fields":[
                {"key":"button_title", "name":_("PAYMENT/HIT_PAY/PAYMENT_BUTTON_TITLE"), "type":"text", "r":0, "c":0, "w":6},
                {"key":"currency", "name":_("PAYMENT/CURRENCY_CODE"), "type":"select", "r":0, "c":1, "options":['SGD','AUD','NTD'], "w":6},
                {"key":"api_key", "name":_("PAYMENT/HIT_PAY/API_KEY"), "type":"password", "r":1, "c":0, "w":12},
                {"key":"salt", "name":_("PAYMENT/HIT_PAY/SALT"), "type":"text", "r":2, "c":0, "w":12}
            ],
            "tab": "HitPay",
            "request_url": "api/user-subscription/hitpay/"
        }
        return hitpay
    
    @classmethod
    def paypal(cls):
        paypal = {
            "multiple":False,
            "fields":[
                {"key":"clientId", "name":_("PAYMENT/PAYPAL/CLIENT_ID"), "type":"text", "r":0, "c":0, "w":6},
                {"key":"currency", "name":_("PAYMENT/CURRENCY_CODE"), "type":"select", "r":0, "c":1, "w":6, "options":['SGD','AUD','NTD']},
                {"key":"secret", "name":_("PAYMENT/PAYPAL/SECRET"), "type":"password", "r":1, "c":0, "w":12},
            ],
            "tab":"PayPal",
            "request_url": "api/user-subscription/paypal/"
        }
        return paypal

    @classmethod
    def stripe(cls):
        stripe = {
            "multiple":False,
            "fields":[
                {"key":"secret", "type":"password", "name":_("PAYMENT/SECRET_KEY"), "r":0, "c":0, "w":6},
                {"key":"currency", "type":"select", "name":_("PAYMENT/CURRENCY_CODE"), "r":0, "c":1, "w":6, "options":[
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
        return stripe

    @classmethod
    def pay_mongo(cls):
        pay_mongo = {
            "multiple":False,
            "fields":[
                {"key":"secret", "name":_("PAYMENT/SECRET_KEY"), "type":"password", "r":0, "c":0, "w":12},
            ],
            "tab":"Pay Mongo",
            "request_url": "api/user-subscription/pay_mongo/"
        }
        return pay_mongo
    
    @classmethod
    def first_data(cls):
        first_data = {
            "multiple":False,
            "fields":[
                {"key":"storeId", "name":_("PAYMENT/FIRST_DATA/STORE_ID"), "type":"text", "r":0, "c":0, "w":6},
                {"key":"sharedSecret", "name":_("PAYMENT/FIRST_DATA/SHARE_SECRET"), "type":"password", "r":0, "c":1, "w":6},
                {"key":"currency", "name":_("PAYMENT/CURRENCY_CODE"), "type":"select", "r":1, "c":0, "w":6, "options":['702', '703']},
                {"key":"timezone", "name":_("PAYMENT/FIRST_DATA/TIME_ZONE"), "type":"select", "r":1, "c":1, "w":6, "options":['Asia/Singapore']}
            ],
            "tab":"First Data IPG (Credit Card)",
            "request_url": "api/user-subscription/first_data/"
        }
        return first_data

    # confirmed list
    SG = ['direct_payment','hitpay','paypal', 'stripe', 'first_data']
    
    ID = ['direct_payment','hitpay','paypal', 'stripe', 'first_data']

    MY = ['direct_payment','paypal', 'stripe']
    
    IN = ['direct_payment','paypal', 'stripe']
    
    PH = ['direct_payment', 'paypal', 'hitpay', 'pay_mongo']
    
    if settings.WEB_SERVER_URL == "https://plusoneapp.sociallab.ph":
        PH = ['direct_payment','paypal']

    
    # not confirmed list
    VN = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    TW = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    CN = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    KH = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    AU = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    HK = ['direct_payment','hitpay','paypal', 'stripe', 'pay_mongo', 'first_data']

    @classmethod
    def get_meta(cls, lang, country_code='SG'):
        with translation.override(lang):
            payment_support_list = getattr(cls,country_code)
            meta = {}
            for payment in payment_support_list:
                meta[payment] = getattr(cls,payment)()
            return meta