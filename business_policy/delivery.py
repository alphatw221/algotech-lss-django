from dataclasses import dataclass
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils import translation

class DeliveryMeta():
    
    ecpay = 'ecpay'
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
    
    # not confirmed list
    SG = []
    VN = []

    TW = [ecpay]

    CN = []

    KH = []

    AU = []

    HK = []

    @classmethod
    def get_support_delivery(cls, country_code='SG'):
        support_delivery_list = getattr(cls,country_code)
        return support_delivery_list