from dataclasses import dataclass
from backend.api._api_caller import RestApiJsonCaller
from django.conf import settings

@dataclass
class TextClassifierApiCaller(RestApiJsonCaller):
    domain_url: str = settings.NLP_COMPUTING_MACHINE_URL
    # domain_url: str = "http://192.168.74.127:8501"

    # TF serveing doesn't accept '/' at the end of the url
    def _get_url(self):
        return f"{self.domain_url}/{f'{self.path}' if self.path else ''}"
