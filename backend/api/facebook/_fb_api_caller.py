from django.conf import settings
from dataclasses import dataclass
from backend.api._api_caller import RestApiJsonCaller


@dataclass
class FacebookApiCaller(RestApiJsonCaller):
    domain_url: str = settings.FACEBOOK_API_URL

@dataclass
class InstagramApiCaller(RestApiJsonCaller):
    domain_url: str = settings.INSTAGRAM_API_URL