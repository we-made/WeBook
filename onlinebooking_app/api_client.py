from typing import Dict, List
import httpx
from config import API_URL, SERVICE_ACCOUNT_USERNAME, SERVICE_ACCOUNT_PASSWORD

import time
import traceback


class RetryTransport(httpx.HTTPTransport):
    def handle_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:
        retry = 0
        resp = None
        while retry < 5:
            retry += 1
            if retry > 2:
                time.sleep(10)
            try:
                if resp is not None:
                    resp.close()
                resp = super().handle_request(request)
            except Exception as e:
                print("httpx {} exception {} caught - retrying".format(request.url, e))
                continue
            if resp.status_code >= 500 and resp.status_code < 600:
                print("httpx {} 5xx response - retrying".format(request.url))
                continue
            content_type = resp.headers.get("Content-Type")
            if content_type is not None:
                mime_type, _, _ = content_type.partition(";")
                if mime_type == "application/json":
                    try:
                        resp.read()
                        resp.json()
                    except Exception as e:
                        traceback.print_exc()
                        print(
                            "httpx {} response not decodable as json '{}' - retrying".format(
                                request.url, e
                            )
                        )
                        continue
            break
        return resp


class WeBookApiAuth(httpx.Auth):
    def __init__(self, username: str, password: str, token_lifetime: int = 600):
        self.username = username
        self.password = password
        self.token_lifetime = token_lifetime
        self._token = None
        self._token_expiry = 0

    def _get_token(self, username: str, password: str):
        if self._token and time.time() < self._token_expiry:
            return self._token

        response: httpx.Response = httpx.post(
            f"{API_URL}/service_accounts/login",
            json={"username": username, "password": password},
        )

        if response.status_code == 200:
            token = response.json()
            self._token = token
            self._token_expiry = time.time() + self.token_lifetime
            return token
        else:
            response.raise_for_status()

    def auth_flow(self, request):
        token = self._get_token(self.username, self.password)
        print(token)
        request.headers["Authorization"] = f"Bearer {token}"
        yield request


class WeBookApiClient(httpx.Client):
    def __init__(self):
        super().__init__(
            base_url=API_URL,
            auth=WeBookApiAuth(SERVICE_ACCOUNT_USERNAME, SERVICE_ACCOUNT_PASSWORD),
            # transport=RetryTransport(),
        )
