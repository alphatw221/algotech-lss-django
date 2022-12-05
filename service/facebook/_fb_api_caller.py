from django.conf import settings
from dataclasses import dataclass
from .._rest_api_json_caller import RestApiJsonCaller

@dataclass
class FacebookApiCaller(RestApiJsonCaller):
    domain_url: str = settings.FACEBOOK_API_URL


@dataclass
class FacebookApiV12Caller(RestApiJsonCaller):
    domain_url: str = settings.FACEBOOK_API_URL_V12


@dataclass
class InstagramApiCaller(RestApiJsonCaller):
    domain_url: str = settings.INSTAGRAM_API_URL
