
from .._rest_api_json_caller import RestApiJsonCaller
from dataclasses import dataclass




@dataclass
class HitPayApiCaller(RestApiJsonCaller):
    domain_url: str = "https://api.hit-pay.com"
    