from django.conf import settings
from dataclasses import dataclass
from .._rest_api_json_caller import RestApiJsonCaller


@dataclass
class YoutubeApiCaller(RestApiJsonCaller):
    domain_url: str = settings.YOUTUBE_API_URL


@dataclass
class GoogleApiCaller(RestApiJsonCaller):
    domain_url: str = settings.GOOGLE_API_URL


@dataclass
class YoutubeGoogleApiCaller(RestApiJsonCaller):
    domain_url: str = "https://youtube.googleapis.com/youtube/v3"
