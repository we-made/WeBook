import asyncio
from datetime import datetime, timedelta
import threading
from typing import Optional
import httpx


class WeBookAuthMiddleware(httpx.Auth):
    def __init__(self, user_name: str, password: str, webook_api_url: str) -> None:

        self.user_name = user_name
        self.password = password

        self.webook_api_url = webook_api_url
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        
        self._sync_lock = None
        self._async_lock = None

    def __get_token(self) -> str:
        if not self.token or datetime.now() > self.token_expiry:
            payload = { 
                "grant_type": "",
                "username": self.user_name, 
                "password": self.password,
                "scope": "",
                "client_id": "",
                "client_secret": "",
            }
            print(payload)
            token_request = httpx.post(self.webook_api_url + "/token", data=payload)
            print(token_request.url)
            if token_request.is_success:
                self.token = token_request.json()["access_token"]
                self.token_expiry = datetime.now() + timedelta(minutes=15)
            else:
                raise Exception(f"Failed with status code {token_request.status_code} when attempting to authenticate with the WeBook API", token_request)
        return self.token

    def sync_get_token(self):
        if not self._sync_lock:
            self._sync_lock = threading.RLock()

        with self._sync_lock:
            return self.__get_token()

    async def async_get_token(self):
        if not self._async_lock:
            self._async_lock = asyncio.Lock()
        
        async with self._async_lock:
            return self.__get_token()

    def sync_auth_flow(self, request):
        token = self.sync_get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request
    
    async def async_auth_flow(self, request):
        token = self.sync_get_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request
