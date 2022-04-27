from django.conf import settings
from datetime import datetime, timedelta, timezone
from api.utils.common.verify import Verify
from api.utils.error_handle.error.api_error import ApiVerifyError

class UserSubscriptionCheckRule():

    @staticmethod
    def is_expired(**kwargs):
        api_user = kwargs.get('api_user')
        user_subscription = Verify.get_user_subscription_from_api_user(api_user)
        if datetime.now().replace(tzinfo=timezone(offset=timedelta())) > user_subscription.expired_at:
            raise ApiVerifyError('Your membership is out of date.')
