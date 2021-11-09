from django.conf import settings
from dataclasses import dataclass
from api.utils.api._api_caller import RestApiJsonCaller


@dataclass
class FacebookApiCaller(RestApiJsonCaller):
    doamin_url: str = settings.FACEBOOK_API_URL


# TODO: implement facebook api module
