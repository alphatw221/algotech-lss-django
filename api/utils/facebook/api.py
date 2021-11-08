from django.conf import settings
from dataclasses import dataclass
from api.utils.common.api.api_caller import RestApiJsonCaller


@dataclass
class FacebookApiCaller(RestApiJsonCaller):
    doamin_url: str = settings.FACEBOOK_API_URL
