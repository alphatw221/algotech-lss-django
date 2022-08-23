from django.conf import settings
from dataclasses import dataclass
from .._rest_api_json_caller import RestApiJsonCaller

@dataclass
class TiktokApiCaller(RestApiJsonCaller):
    domain_url: str = "https://ads.tiktok.com"
    
class TiktokBusinessApiCaller(RestApiJsonCaller):
    domain_url: str = "https://business-api.tiktok.com"

