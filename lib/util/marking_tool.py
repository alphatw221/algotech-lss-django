from abc import abstractclassmethod
from django.conf import settings
import business_policy
from business_policy.marketing_plan import MarketingPlan
import service
from lib.util import verify
class MetaMark():

    mark_key = ""
    mark_value = ""

    @classmethod
    def mark(cls, model, save=False, mark_value=None):
        try:
            if mark_value == None:
                model.meta[cls.mark_key] = cls.mark_value
            else:
                model.meta[cls.mark_key] = mark_value
            if save:
                model.save()
        except Exception:
            pass
    
    @classmethod
    def _get_mark(cls, model):
        try:
            return model.meta.get(cls.mark_key)
        except Exception:
            pass
        return None

    @classmethod
    def _erase_mark(cls, model, save=False):
        try:
            del model.meta[cls.mark_key]
            if save:
                model.save()
        except Exception:
            pass

    @abstractclassmethod
    def check_mark(cls):
        pass


class NewUserMark(MetaMark):

    mark_key = "new_user"
    mark_value = True
    
    @classmethod
    def check_mark(cls, api_user, save=False):
        try:
            if not cls._get_mark(api_user):
                return
            
            user_subscription = verify.Verify.get_user_subscription_from_api_user(api_user)

            country_plan = business_policy.subscription_plan.SubscriptionPlan.get_country(user_subscription.country)
            service.sendinblue.transaction_email.WelcomeEmail(
                first_name=api_user.name,
                to=[api_user.email],
                cc=country_plan.cc,
                country=user_subscription.country).send()

            cls._erase_mark(api_user, save = save)
        except Exception as e:
            pass
        
class WelcomeGiftUsedMark(MetaMark):

    mark_key = "welcome_gift_used"
    mark_value = True
    
    @classmethod
    def check_mark(cls, api_user, original_price):
        try:
            if cls._get_mark(api_user) != False:
                return original_price
            # cls.mark(api_user, save=True)
            discount_rate = MarketingPlan.welcome_gift().get('discount_rate')
            return original_price * discount_rate
        except Exception as e:
            pass        
