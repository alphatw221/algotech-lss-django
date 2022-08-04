import pytz
from lib.error_handle.error.api_error import ApiVerifyError
from django.contrib.auth.models import User as AuthUser
from api.models.user.user import User
import lib
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
    def has_email_been_registered_as_seller(**kwargs):
        email = kwargs.get('email')
        if User.objects.filter(email=email, type='user').exists():
            raise ApiVerifyError('This email address has already been registered.')

    @staticmethod
    def is_email_format_valid(**kwargs):
        email = kwargs.get('email')
        if type(email) != str:
            raise ApiVerifyError('invalid email')
        return {"email":email.lower().replace(" ","")}
        
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



    @classmethod
    def is_new_password_valid(cls, **kwargs):
        new_password = kwargs.get('new_password')
        if not (type(new_password)==str and len(new_password)>=8 and len(new_password)<=20):
            raise lib.error_handle.error.api_error.ApiVerifyError('invalid password')