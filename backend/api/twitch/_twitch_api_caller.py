from django.conf import settings
from dataclasses import dataclass
from backend.api._api_caller import RestApiJsonCaller

@dataclass
class TwitchOAUTHApiCaller(RestApiJsonCaller):
    domain_url: str = settings.TWITCH_OAUTH_API_URL