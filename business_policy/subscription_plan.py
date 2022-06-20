from api.utils.error_handle.error.api_error import ApiVerifyError


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
            "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":90,"year":324}},
            "premium" : {"text": "Premium", "price":{"quarter":180,"year":648}},
        }
        
    class PH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app', 'hello@liveshowseller.ph']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
             "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":54,"year":194}},
            "premium" : {"text": "Premium", "price":{"quarter":120,"year":432}},
        }
    
    class TH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":75,"year":270}},
            "premium" : {"text": "Premium", "price":{"quarter":126,"year":454}},
        }

    class IN(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":75,"year":270}},
            "premium" : {"text": "Premium", "price":{"quarter":126,"year":454}},
        }

        

    class ID(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "id"
        cc = ['lss@algotech.app', 'contact@liveshowseller.id']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":90,"year":324}},
            "premium" : {"text": "Premium", "price":{"quarter":180,"year":648}},
        }
    
    class MY(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":90,"year":324}},
            "premium" : {"text": "Premium", "price":{"quarter":180,"year":648}},
        }

    class VN(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":54,"year":194}},
            "premium" : {"text": "Premium", "price":{"quarter":120,"year":432}},
        }

    class TW(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "TWD"
        language = "zh_hant"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":900,"year":3240}},
            "standard" : {"text": "Standard", "price":{"quarter":2700,"year":9720}},
            "premium" : {"text": "Premium", "price":{"quarter":5400,"year":19440}},
        }
   

    class KH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        cc = ['lss@algotech.app']
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":54,"year":194}},
            "premium" : {"text": "Premium", "price":{"quarter":120,"year":432}},
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
        'products_limit': 10,
        'orders_limit': 100
    }
    lite = {
        'campaign_limit':0,
        'campaign_live_limit': 2,
        'channel_limit': 1,
        'products_limit': 30,
        'orders_limit': 300
    }
    standard = {
        'campaign_limit':0,
        'campaign_live_limit': 4,
        'channel_limit': 2,
        'products_limit': 100,
        'orders_limit': 1000
    }
    premium = {
        'campaign_limit':0,
        'campaign_live_limit': 6,
        'channel_limit': 3,
        'products_limit': 300,
        'orders_limit': 5000
    }
    dealer = {
        'campaign_limit':0,
        'campaign_live_limit': 100,
        'channel_limit': 30,
        'products_limit': 3000,
        'orders_limit': 500000
    } 