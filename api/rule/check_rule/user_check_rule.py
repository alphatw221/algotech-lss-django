import pytz
from api.utils.error_handle.error.api_error import ApiVerifyError
from django.contrib.auth.models import User as AuthUser
from api.models.user.user import User

class AdminCheckRule():

    @staticmethod
    def is_role_valid_for_creation(**kwargs):
        role = kwargs.get('role')
        if role not in ['seller','dealer']:
            raise ApiVerifyError('invalid role')

class DealerCheckRule():

    @staticmethod
    def is_dealer_status_valid(**kwargs):
        dealer_user_subscription = kwargs.get('dealer_user_subscription')
        if dealer_user_subscription.status not in ['new', 'renew', 'valid']:
            raise ApiVerifyError('dealer status invalid')
    
    @staticmethod
    def is_dealer_license_sufficient(**kwargs):
        dealer_user_subscription = kwargs.get('dealer_user_subscription')
        months = kwargs.get('months')

        #TODO check is_dealer_license_sufficient


class UserCheckRule():

    @staticmethod
    def is_timezone_valid(**kwargs):
        timezone = kwargs.get('timezone')
        if ((timezone != "") and (timezone not in pytz.all_timezones)):
            raise ApiVerifyError("Time Zone is not a valid format.")
    @staticmethod
    def has_email_been_registered(**kwargs):
        email = kwargs.get('email')
        if AuthUser.objects.filter(email = email).exists() or User.objects.filter(email=email, type='user').exists():
            raise ApiVerifyError('This email address has already been registered.')

    @staticmethod
    def is_plan_valid(**kwargs):
        pass
        #TODO check is_dealer_license_sufficient
        # raise ApiVerifyError()

    @staticmethod
    def is_months_valid(**kwargs):
        months = kwargs.get('months')

        if type(months) != int:
            raise ApiVerifyError('data type of months invalid')
        
        if months>12 or months <1:
            raise ApiVerifyError('months invalid')
    
    
    @staticmethod
    def is_activated_country_valid(**kwargs):
        pass
        #TODO check is_dealer_license_sufficient
        # raise ApiVerifyError()

    @staticmethod
    def is_password_valid(**kwargs):
        password = kwargs.get('password')
        pass

    @staticmethod
    def is_new_password_valid(**kwargs):
        new_password = kwargs.get('new_password')
        pass