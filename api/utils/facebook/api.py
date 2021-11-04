from django.conf import settings
from dataclasses import dataclass
import requests


@dataclass
class FacebookAPI:
    url: str
    bearer_token: str = None

    def __post_init__(self):
        self.url = f'{settings.FACEBOOK_API_URL}/{self.url}'
        self.params = {}
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json'}
        self.data = {}

        if self.bearer_token:
            self.headers['Authorization'] = (f'Bearer {self.bearer_token}')

    def get(self):
        response = requests.get(
            f"{self.url}/jobs", params=self.params, headers=self.headers)
        return response.json()

    def post(self):
        response = requests.post(
            f"{self.url}/jobs", params=self.params, headers=self.headers, data=self.data)
        return response.json()
