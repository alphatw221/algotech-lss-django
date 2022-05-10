
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from ._sendinblue import api_client

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)



class TransactionEmail():

    template_module = None
    template_name = None

    def __init__(self, to=None, cc=None, country="",template_id=None, params=None):
        self.to = to
        self.cc = cc
        self.country = country
        self.template_id = template_id
        self.params = params

    def send(self):
        try:
            to = [{"email":self.to}]
            cc = [{"email":self.cc}]
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    template_id=self._get_template_id(),
                    to=to, 
                    cc=cc if self.cc else None, 
                    params=self.params)
        
            api_instance.send_transac_email(send_smtp_email)
        except ApiException as e:
            print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

    def _get_template_id(self):
        if self.template_id:
            return int(self.template_id)

        template_name = f"{self.template_name}_{self.country}" if self.country else self.template_name
        return getattr(self.template_module, template_name)