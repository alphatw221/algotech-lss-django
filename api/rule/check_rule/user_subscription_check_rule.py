from api import models
import lib
from backend.pymongo.mongodb import db
from django.conf import settings
from datetime import datetime, timedelta, timezone
import arrow

class UserSubscriptionCheckRule():

    @staticmethod
    def is_expired(**kwargs):
        user_subscription = kwargs.get('user_subscription')
        subscription_expired_at = arrow.get(user_subscription.expired_at)
        
        if arrow.utcnow() > subscription_expired_at:
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.membership_out_of_date')
    
    @staticmethod
    def max_concurrent_live(**kwargs):

        user_subscription = kwargs.get('user_subscription')
        if user_subscription.status == models.user.user_subscription.STATUS_TEST:
            return 
        now = arrow.utcnow().datetime
        live_count = user_subscription.campaigns.filter(start_at__lte=now, end_at__gte=now).count()
        if not user_subscription.campaign_live_limit:
            return
        if live_count >= user_subscription.campaign_live_limit:
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.reach_max_concurrent_campaigns')
        
    @staticmethod
    def campaign_limit(**kwargs):

        user_subscription = kwargs.get('user_subscription')
        if user_subscription.status == models.user.user_subscription.STATUS_TEST:
            return 
        campaigns_count = user_subscription.campaigns.filter(created_at__gte=user_subscription.started_at).count() 
        if not user_subscription.campaign_limit:
            return
        if campaigns_count >= user_subscription.campaign_limit:
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.reach_max_campaigns_limit')
        
    def campaign_end_time_over_subscription_period(**kwargs):
        user_subscription = kwargs.get('user_subscription')
        if not kwargs.get('campaign_data',{}).get('end_at'):
            return
        end_at = arrow.get(kwargs.get('campaign_data',{}).get('end_at'))
        subscription_expired_at = arrow.get(user_subscription.expired_at)
        if end_at > subscription_expired_at:
            raise lib.error_handle.error.api_error.ApiVerifyError('helper.campaign_end_time_not_later_subscription_period', {"datetime_subscription_expired_at": subscription_expired_at.format('YYYY-MM-DD HH:mm:ss ZZ')})