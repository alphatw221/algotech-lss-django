from api.utils.error_handle.error.api_error import ApiVerifyError


class CountryPlan:

    @classmethod
    def get_plan(cls,plan):
        subscription_plan = cls.plans.get(plan)
        if not subscription_plan:
            raise ApiVerifyError("invalid subscription plan")
        return subscription_plan
class SubscriptionPlan: 

    @classmethod
    def get_country(cls,country_code):
        country_plan = getattr(cls,country_code, None)
        if not country_plan or type(country_plan)!=type:
            raise ApiVerifyError("invalid country")
        return country_plan


    class SG(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
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
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":90,"year":324}},
            "premium" : {"text": "Premium", "price":{"quarter":180,"year":648}},
        }
    
    class TH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
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
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":54,"year":194}},
            "premium" : {"text": "Premium", "price":{"quarter":120,"year":432}},
        }

    class TW(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "NTD"
        language = "zh_hant"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":900,"year":3240}},
            "standard" : {"text": "Standard", "price":{"quarter":1800,"year":6480}},
            "premium" : {"text": "Premium", "price":{"quarter":2700,"year":9720}},
        }
   

    class KH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"month":0}},
            "lite" : {"text": "Lite", "price":{"quarter":30,"year":108}},
            "standard" : {"text": "Standard", "price":{"quarter":54,"year":194}},
            "premium" : {"text": "Premium", "price":{"quarter":120,"year":432}},
        }
