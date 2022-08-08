from api.utils.error_handle.error.api_error import ApiVerifyError
from . import subscription

class CountryPlan:

    @classmethod
    def get_plan(cls,plan):
        subscription_plan = cls.plans.get(plan)
        if not subscription_plan:
            raise ApiVerifyError("invalid subscription plan")
        return subscription_plan
class SubscriptionPlan: 

    support_country=['SG', 'PH', 'TH', 'IN', 'ID', 'MY', 'VN', 'TW', 'KH']
    support_plan=['trial', 'lite', 'standard', 'premium', 'dealer']

    @classmethod
    def get_country(cls,country_code):
        if country_code not in cls.support_country:
            raise ApiVerifyError("invalid country")
        return getattr(cls,country_code, None)


    class SG(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"value":"lite", "text": "Lite", "price":{"month":10,"quarter":30,"year":108}},
            "standard" : {"value":"standard","text": "Standard", "price":{"month":30,"quarter":90,"year":324}},
            "premium" : {"value":"premium","text": "Premium", "price":{"month":15,"quarter":45,"year":162}},
        }
        
    class PH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app', 'hello@liveshowseller.ph']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"value":"lite","text": "Lite", "price":{"month":10,"quarter":30,"year":108}},
            "standard" : {"value":"standard","text": "Standard", "price":{"month":18,"quarter":54,"year":194}},
            "premium" : {"value":"premium","text": "Premium", "price":{"month":10,"quarter":30,"year":108}},
        }
    
    class TH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"value":"lite","text": "Lite", "price":{"month":10,"quarter":30,"year":108}},
            "standard" : {"value":"standard","text": "Standard", "price":{"month":30,"quarter":90,"year":324}},
            "premium" : {"value":"premium","text": "Premium", "price":{"month":15,"quarter":45,"year":162}},
        }

    class IN(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"value":"lite","text": "Lite", "price":{"month":10,"quarter":30,"year":108}},
            "standard" : {"value":"standard","text": "Standard", "price":{"month":30,"quarter":90,"year":324}},
            "premium" : {"value":"premium","text": "Premium", "price":{"month":15,"quarter":45,"year":162}},
        }

        

    class ID(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "id"
        cc = ['lss@algotech.app', 'contact@liveshowseller.id']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"value":"lite","text": "Lite", "price":{"month":10,"quarter":30,"year":108}},
            "standard" : {"value":"standard","text": "Standard", "price":{"month":25,"quarter":75,"year":270}},
            "premium" : {"value":"premium","text": "Premium", "price":{"month":10,"quarter":30,"year":108}},
        }
    
    class MY(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"value":"lite","text": "Lite", "price":{"month":10,"quarter":30,"year":108}},
            "standard" : {"value":"standard","text": "Standard", "price":{"month":30,"quarter":90,"year":324}},
            "premium" : {"value":"premium","text": "Premium", "price":{"month":15,"quarter":45,"year":162}},
        }

    class VN(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "VND"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"value":"lite","text": "Lite", "price":{"month":70000,"quarter":210000,"year":765000}},
            "standard" : {"value":"standard","text": "Standard", "price":{"month":160000,"quarter":480000,"year":1728000}},
            "premium" : {"value":"premium","text": "Premium", "price":{"month":100000,"quarter":300000,"year":1080000}},
        }

    class TW(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "TWD"
        language = "zh_hant"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"value":"lite","text": "Lite", "price":{"month":300,"quarter":900,"year":3240}},
            "standard" : {"value":"standard","text": "Standard", "price":{"month":900,"quarter":2700,"year":9720}},
            "premium" : {"value":"premium","text": "Premium", "price":{"month":450,"quarter":1350,"year":4860}},
        }
   

    class KH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"value":"lite","text": "Lite", "price":{"month":10,"quarter":30,"year":108}},
            "standard" : {"value":"standard","text": "Standard", "price":{"month":30,"quarter":90,"year":324}},
            "premium" : {"value":"premium","text": "Premium", "price":{"month":15,"quarter":45,"year":162}},
        }

    @classmethod
    def get_plan_limit(cls,plan):
        if plan not in cls.support_plan:
            raise ApiVerifyError("invalid subscription plan")
        return getattr(cls, plan)

    trial = {
        'campaign_limit':5,
        'campaign_live_limit': 2,
        'channel_limit': 1,
        'product_limit': 10,
        'order_limit': 100
    }
    lite = {
        'campaign_limit':0,
        'campaign_live_limit': 2,
        'channel_limit': 1,
        'product_limit': 30,
        'order_limit': 300
    }
    standard = {
        'campaign_limit':0,
        'campaign_live_limit': 4,
        'channel_limit': 2,
        'product_limit': 100,
        'order_limit': 1000
    }
    premium = {
        'campaign_limit':0,
        'campaign_live_limit': 6,
        'channel_limit': 3,
        'product_limit': 300,
        'order_limit': 5000
    }
    dealer = {
        'campaign_limit':0,
        'campaign_live_limit': 100,
        'channel_limit': 30,
        'product_limit': 3000,
        'order_limit': 500000
    } 