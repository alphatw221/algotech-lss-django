from datetime import datetime, timedelta, timezone
from api.utils.common.verify import Verify
from api.utils.error_handle.error.api_error import ApiVerifyError
from backend.pymongo.mongodb import db
from datetime import datetime

class UserSubscriptionCheckRule():

    @staticmethod
    def is_expired(**kwargs):
        api_user = kwargs.get('api_user')
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        if datetime.now().replace(tzinfo=timezone(offset=timedelta())) > user_subscription.expired_at:
            raise ApiVerifyError('Your membership is out of date.')
    
    @staticmethod
    def campaigns_limit(**kwargs):
        api_user = kwargs.get('api_user')
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        plan, subscription_id = user_subscription.type, user_subscription.id
        campaign_count = db.api_campaign.find({'$or': [{'start_at': {'$lte': datetime.now()}, 'end_at': {'$gte': datetime.now()}}, {'start_at': {'$gte': datetime.now()}}], 'user_subscription_id': int(subscription_id)}).count()

        if (plan == 'trial' or plan == 'lite') and campaign_count >= 2:
            raise ApiVerifyError('You\'ve been reached maximum campaign.')
        elif plan == 'standard' and campaign_count >= 4:
            raise ApiVerifyError('You\'ve been reached maximum campaign.')
        elif plan == 'premium' and campaign_count >= 6:
            raise ApiVerifyError('You\'ve been reached maximum campaign.')