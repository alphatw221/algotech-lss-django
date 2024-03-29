from dataclasses import dataclass, field
import requests
import logging

logger = logging.getLogger(__name__)


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
        return self.__request_template(requests.get,
                                       headers=self.headers,
                                       params=self.params,
                                       timeout=5
                                       )

    def post(self):
        return self.__request_template(requests.post,
                                       headers=self.headers,
                                       params=self.params,
                                       json=self.data,
                                       timeout=5
                                       )

    def delete(self):
        return self.__request_template(requests.delete,
                                       headers=self.headers,
                                       params=self.params,
                                       json=self.data,
                                       timeout=5
                                       )
        
    def _process_response(self, response):
        if response.status_code // 100 == 2:
            ...  # handels status code 2XX
        else:
            logger.warning(
                f'Not 2XX HTTP Response:\n'
                f'{response.request.headers=}, {response.request.body=}, \n'
                f'{response.status_code=}, {response.text=}'
            )

    def _format_response(self, response):
        try:
            return response.status_code, response.json()
        except Exception:
            return response.status_code, {'Invalid json response': response.text}

    def __request_template(self, request_func, *args, **kwargs):
        try:
            response = request_func(url=self._get_url(), *args, **kwargs)
            self._process_response(response)
            return self._format_response(response)
        except Exception as e:
            return 0, {'RestApiJsonCaller error': e}

    def _get_url(self):
        return f"{self.domain_url}/{f'{self.path}' if self.path else ''}"
