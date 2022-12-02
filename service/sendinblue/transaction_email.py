from ._transaction_email import TransactionEmail
from . import template

class ResetPasswordLinkEmail(TransactionEmail):
    template_module = template.password
    template_name = "RESET_PASSWORD_LINK"

    def __init__(self, url, code, username, to=None, cc=None, country="", lang=""):
        super().__init__(to, cc, country)
        self.params = {
            "url":url,
            "code":code,
            "username":username
        }

class AccountActivationEmail(TransactionEmail):
    template_module = template.registration
    template_name = "ACTIVATION"

    def __init__(self, first_name, plan, email, password, to=None, cc=None, country="", lang=""):
        super().__init__(to, cc, country, lang)
        self.params = {
            "first_name":first_name,
            "plan":plan,
            "email":email,
            "password":password
        }

class WelcomeEmail(TransactionEmail):
    template_module = template.login
    template_name = "WELCOME"

    def __init__(self, first_name, to=None, cc=None, country="", lang=""):
        super().__init__(to, cc, country, lang)
        self.params = {
            "first_name":first_name
        }

class OrderConfirmationEmail(TransactionEmail):
    template_module = template.orderconfirmation
    template_name = "ORDER_CONFIRMATION"

    def __init__(self, shop, order, campaign, to=None, cc=None, country="", lang=""):
        super().__init__(to, cc, country, lang)
        self.params = {
            "shop": shop,
            "order": order,
            "campaign": campaign
        }