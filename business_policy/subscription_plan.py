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
            "trial" :{"text": "Free Trial", "price":{"monthly":0}},
            "lite" : {"text": "Lite", "price":{"monthly":10,"quarterly":30}},
            "standard" : {"text": "Standard", "price":{"monthly":30,"quarterly":90}},
            "premium" : {"text": "Premium", "price":{"monthly":60,"quarterly":180}},
        }
        
    class PH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"monthly":0}},
            "lite" : {"text": "Lite", "price":{"monthly":10,"quarterly":30}},
            "standard" : {"text": "Standard", "price":{"monthly":30,"quarterly":90}},
            "premium" : {"text": "Premium", "price":{"monthly":60,"quarterly":180}},
        }
    
    class TH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"monthly":0}},
            "lite" : {"text": "Lite", "price":{"monthly":10,"quarterly":30}},
            "standard" : {"text": "Standard", "price":{"monthly":25,"quarterly":75}},
            "premium" : {"text": "Premium", "price":{"monthly":42,"quarterly":126}},
        }

    class IN(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"monthly":0}},
            "lite" : {"text": "Lite", "price":{"monthly":10,"quarterly":30}},
            "standard" : {"text": "Standard", "price":{"monthly":25,"quarterly":75}},
            "premium" : {"text": "Premium", "price":{"monthly":42,"quarterly":126}},
        }
        

    class ID(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "id"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"monthly":0}},
            "lite" : {"text": "Lite", "price":{"monthly":10,"quarterly":30}},
            "standard" : {"text": "Standard", "price":{"monthly":30,"quarterly":90}},
            "premium" : {"text": "Premium", "price":{"monthly":60,"quarterly":180}},
        }
    
    class MY(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"monthly":0}},
            "lite" : {"text": "Lite", "price":{"monthly":10,"quarterly":30}},
            "standard" : {"text": "Standard", "price":{"monthly":30,"quarterly":90}},
            "premium" : {"text": "Premium", "price":{"monthly":60,"quarterly":180}},
        }

    class VN(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"monthly":0}},
            "lite" : {"text": "Lite", "price":{"monthly":10,"quarterly":30}},
            "standard" : {"text": "Standard", "price":{"monthly":18,"quarterly":54}},
            "premium" : {"text": "Premium", "price":{"monthly":40,"quarterly":120}},
        }

    class TW(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "TWD"
        language = "zh_hant"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"monthly":0}},
            "lite" : {"text": "Lite", "price":{"monthly":300,"quarterly":900}},
            "standard" : {"text": "Standard", "price":{"monthly":600,"quarterly":1800}},
            "premium" : {"text": "Premium", "price":{"monthly":900,"quarterly":2700}},
        }

    class CH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "zh_hans"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"monthly":0}},
            "lite" : {"text": "Lite", "price":{"monthly":10,"quarterly":30}},
            "standard" : {"text": "Standard", "price":{"monthly":30,"quarterly":90}},
            "premium" : {"text": "Premium", "price":{"monthly":60,"quarterly":180}},
        }

    class KH(CountryPlan):
        promo_code="ALGOTECH"
        promo_discount_rate=0.9
        currency = "USD"
        language = "en"
        plans = {
            "trial" :{"text": "Free Trial", "price":{"monthly":0}},
            "lite" : {"text": "Lite", "price":{"monthly":10,"quarterly":30}},
            "standard" : {"text": "Standard", "price":{"monthly":18,"quarterly":54}},
            "premium" : {"text": "Premium", "price":{"monthly":40,"quarterly":120}},
        }