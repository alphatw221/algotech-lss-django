from dataclasses import dataclass
from backend.api._api_caller import RestApiJsonCaller
from django.conf import settings


class HitPay_Helper:

    @dataclass
    class HitPayApiCaller(RestApiJsonCaller):
        domain_url: str = settings.HITPAY_API_URL
