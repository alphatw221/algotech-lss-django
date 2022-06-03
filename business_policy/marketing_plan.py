from api.utils.error_handle.error.api_error import ApiVerifyError


class MarketingPlan:
    current_plans = ['welcome_gift']
    @classmethod
    def get_plans(cls, plan_type):
        plans = getattr(cls, plan_type)
        meta = {}
        for plan in plans:
            meta[plan] = getattr(cls,plan)()
        return meta

    @classmethod
    def welcome_gift(cls):
        return {
            "name": "Welcome Gift",
            "expire_time": None,
            "discount_rate":0.95,
            "description": "5% discount for fisrt time pay."
        }
    
   