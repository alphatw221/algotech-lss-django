from django.conf import settings
from dataclasses import dataclass
from .._rest_api_json_caller import RestApiJsonCaller


@dataclass
class TwitchApiCaller(RestApiJsonCaller):
    domain_url: str = settings.TWITCH_API_URL

@dataclass
class TwitchOauthCaller(RestApiJsonCaller):
    domain_url: str = settings.TWITCH_OAUTH_URL