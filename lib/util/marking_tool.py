from abc import abstractclassmethod
from django.conf import settings
from api.utils.common.verify import Verify
import service

class MetaMark():

    mark_key = ""
    mark_value = ""

    @classmethod
    def mark(cls, model, save=False):
        try:
            model.meta[cls.mark_key] = cls.mark_value
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
            
            user_subscription = Verify.get_user_subscription_from_api_user(api_user)
            # service.sendinblue.transaction_email.WelcomeEmail(
            #     first_name=api_user.name,
            #     to=[api_user.email],
            #     cc=[settings.NOTIFICATION_EMAIL],
            #     lang=user_subscription.lang).send()
            print('first login')

            cls._erase_mark(api_user, save = save)
        except Exception as e:
            pass
        