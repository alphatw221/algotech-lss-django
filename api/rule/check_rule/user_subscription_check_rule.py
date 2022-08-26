import lib
from backend.pymongo.mongodb import db
from django.conf import settings
from datetime import datetime, timedelta, timezone

class UserSubscriptionCheckRule():

    @staticmethod
    def is_expired(**kwargs):
        print("------------is_expired")
        user_subscription = kwargs.get('user_subscription')
        if datetime.now().replace(tzinfo=timezone(offset=timedelta())) > user_subscription.expired_at:
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.membership_out_of_date')
    
    @staticmethod
    def max_concurrent_live(**kwargs):

        user_subscription = kwargs.get('user_subscription')
        now = datetime.now()
        live_count = user_subscription.campaigns.filter(start_at__lte=now, end_at__gte=now).count()  
        if not user_subscription.campaign_live_limit:
            return
        if live_count >= user_subscription.campaign_live_limit:
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.reach_max_concurrent_campaigns')
        
    @staticmethod
    def campaign_limit(**kwargs):

        user_subscription = kwargs.get('user_subscription')
        campaigns_count = user_subscription.campaigns.filter(created_at__gte=user_subscription.started_at).count() 
        if not user_subscription.campaign_limit:
            return
        if campaigns_count >= user_subscription.campaign_limit:
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.reach_max_campaigns_limit')