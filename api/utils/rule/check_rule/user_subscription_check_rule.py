from api.utils.common.verify import Verify
from api.utils.error_handle.error.api_error import ApiVerifyError
from backend.pymongo.mongodb import db
from django.conf import settings
from datetime import datetime, timedelta, timezone
import business_policy.plan_limitation as business_limitation

class UserSubscriptionCheckRule():

    @staticmethod
    def is_expired(**kwargs):
        api_user = kwargs.get('api_user')
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        if datetime.now().replace(tzinfo=timezone(offset=timedelta())) > user_subscription.expired_at:
            raise ApiVerifyError('Your membership is out of date.')
    
    @staticmethod
    def max_concurrent_live(**kwargs):
        api_user = kwargs.get('api_user')
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        plan, subscription_id = user_subscription.type, user_subscription.id
        campaigns_count = db.api_campaign.find({'$or': [{'start_at': {'$lte': datetime.now()}, 'end_at': {'$gte': datetime.now()}}, {'start_at': {'$gte': datetime.now()}}], 'user_subscription_id': int(subscription_id)}).count()

        if settings.GCP_API_LOADBALANCER_URL == 'https://sb.liveshowseller.ph':
            plan_limitation = getattr(business_limitation.social_lab, plan)
        else:
            plan_limitation = getattr(business_limitation.live_show_seller, plan)     

        if campaigns_count >= plan_limitation.get('max_concurrent_live'):
            raise ApiVerifyError('You have reached this maximum allowed number of concurrent campaigns.')
        
    @staticmethod
    def campaign_limit(**kwargs):
        api_user = kwargs.get('api_user')
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        plan = user_subscription.type
        campaigns = user_subscription.campaigns.filter(id__isnull=False)
        
        if settings.GCP_API_LOADBALANCER_URL == 'https://sb.liveshowseller.ph':
            plan_limitation = getattr(business_limitation.social_lab, plan)
        else:
            plan_limitation = getattr(business_limitation.live_show_seller, plan)   
        
        if plan == "trial":
            campaigns_count = campaigns.filter(created_at__gte=user_subscription.started_at).count()
            if campaigns_count >= plan_limitation.get('campaign_limit'):
                raise ApiVerifyError('You have reached the maximum campaign limit')