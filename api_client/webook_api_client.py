from typing import Generator, Optional, Union

import httpx
from httpcore import HTTP2Connection

from api_client.transport import RetryTransport
from api_client.webook_auth import WeBookAuthMiddleware


class WebookAPIClient:
    """A dead simple WeBook v1 API client based on HTTPX fit for purpose"""

    def __init__(
        self,
        api_url,
        user_name,
        password,
        http2: Optional[bool] = True,
    ) -> None:

        self.api_url = api_url

        self.httpx_client = httpx.Client(
            base_url=api_url,
            auth=WeBookAuthMiddleware(
                user_name=user_name, password=password, webook_api_url=api_url
            ),
            headers={"Content-Type": "application/json"},
            transport=RetryTransport(),
            timeout=900,
            http2=http2,
        )

    def _evaluate_response(self, response):
        if response.is_success:
            return response.json()
        else:
            raise Exception(
                f"Request failed with status code {response.status_code}", response
            )

    def get_list(self, endpoint):
        entities = []

        limit = 1000
        offset = 0

        while True:
            response_data = self._evaluate_response(
                self.httpx_client.get(f"v1/{endpoint}?limit={limit}&offset={offset}")
            )

            if len(response_data) == 0:
                break

            entities += response_data
            offset += limit

        return entities

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.httpx_client.close()
