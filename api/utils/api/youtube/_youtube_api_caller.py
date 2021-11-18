from django.conf import settings
from dataclasses import dataclass
from api.utils.api._api_caller import RestApiJsonCaller


@dataclass
class YoutubeApiCaller(RestApiJsonCaller):
    domain_url: str = settings.YOUTUBE_API_URL
