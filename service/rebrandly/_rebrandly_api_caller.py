from django.conf import settings
from dataclasses import dataclass
from .._rest_api_json_caller import RestApiJsonCaller
import requests
import json

@dataclass
class RebrandlyApiCaller(RestApiJsonCaller):
    domain_url: str = "https://api.rebrandly.com"
 

def load_response(response):

    if (response.status_code != requests.codes.ok):
        return False, response.json()
    return True, response.json()


def get_headers():
    header = {
        'Content-Type': 'application/json',
        "apikey": settings.REBRANDLY_API_KEY,
    }

    return header

domain_url = "https://api.rebrandly.com"