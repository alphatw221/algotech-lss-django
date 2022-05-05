from ._transaction_email import TransactionEmail
from . import template


class ResetPasswordLinkEmail(TransactionEmail):
    template_module = template.password
    template_name = "RESET_PASSWORD_LINK"

    def __init__(self, url, code, username, to=None, cc=None, country=""):
        super().__init__(to, cc, country)
        self.params = {
            "url":url,
            "code":code,
            "username":username
        }

class RegistraionConfirmationEmail(TransactionEmail):
    template_module = template.registration
    template_name = "CONFIRMATION"

    def __init__(self, first_name, email, password, to=None, cc=None, country=""):
        super().__init__(to, cc, country)
        self.params = {
            "first_name":first_name,
            "email":email,
            "password":password
        }

class AccountActivationEmail(TransactionEmail):
    template_module = template.registration
    template_name = "ACTIVATION"

    def __init__(self, first_name, plan, email, password, to=None, cc=None, country=""):
        super().__init__(to, cc, country)
        self.params = {
            "first_name":first_name,
            "plan":plan,
            "email":email,
            "password":password
        }
