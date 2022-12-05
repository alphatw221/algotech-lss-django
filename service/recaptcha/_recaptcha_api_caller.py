from dataclasses import dataclass
from .._rest_api_json_caller import RestApiJsonCaller

@dataclass
class RecaptchaApiCaller(RestApiJsonCaller):
    domain_url: str = "https://www.google.com/recaptcha/api/siteverify"


    def _get_url(self):
        return f"{self.domain_url}{f'/{self.path}' if self.path else ''}"