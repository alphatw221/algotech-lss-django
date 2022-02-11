from django.conf import settings
from dataclasses import dataclass
from backend.api._api_caller import RestApiJsonCaller

@dataclass
class GoogleApiCaller(RestApiJsonCaller):
    domain_url: str = settings.GOOGLE_API_URL

@dataclass
class GoogleAccountApiCaller(RestApiJsonCaller):
    domain_url: str = "https://accounts.google.com"

@dataclass
class GoogleOauth2ApiCaller(RestApiJsonCaller):
    domain_url: str = "https://oauth2.googleapis.com"