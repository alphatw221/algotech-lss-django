from dataclasses import dataclass, field
import requests


@dataclass
class RestApiJsonCaller:
    """Simplifying the usage of requests library. Inherent this class and override the `doamin_url`.
    Returns:
        Tuple[int, dict]: Response code and the json dict for the response (text if failed to parse to json).
    """

    path: str = ''
    bearer_token: str = ''
    headers: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    domain_url: str = "https://postman-echo.com"

    def __post_init__(self):
        self.headers['Content-Type'] = 'application/json'
        self.headers['Accept'] = 'application/json'
        if self.bearer_token:
            self.headers['Authorization'] = f'Bearer {self.bearer_token}'

    def get(self):
        response = requests.get(self._get_url(),
                                headers=self.headers,
                                params=self.params,)
        return self._jsonify_response(response)

    def post(self):
        response = requests.post(self._get_url(),
                                 headers=self.headers,
                                 params=self.params,
                                 data=self.data,)
        return self._jsonify_response(response)

    def _get_url(self):
        return f"{self.domain_url}/{f'{self.path}/' if self.path else ''}"

    def _jsonify_response(self, response):
        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {'Invalid json response': response.text}
