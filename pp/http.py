from __future__ import annotations

import os
from typing import Any

import httpx

from pp import session
from pp.errors import AuthError, NetworkError, NotFoundError, UpstreamError

DEFAULT_BASE = "https://api.pushpress.com"


class PPClient:
    def __init__(self, token: str, base_url: str | None = None, timeout: float = 30.0):
        self.base_url = (base_url or os.environ.get("PP_API_BASE") or DEFAULT_BASE).rstrip("/")
        self._client = httpx.Client(
            timeout=timeout,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )

    def _request(self, method: str, path: str, **kw) -> Any:
        url = self.base_url + path
        try:
            resp = self._client.request(method, url, **kw)
        except httpx.RequestError as e:
            raise NetworkError(f"request failed: {e}") from e
        if resp.status_code in (401, 403):
            raise AuthError("unauthorized", detail=f"{resp.status_code} {path}", hint="run: pp login")
        if resp.status_code == 404:
            raise NotFoundError("not found", detail=path)
        if resp.status_code >= 400:
            raise UpstreamError("api error", detail=f"{resp.status_code}: {resp.text[:200]}")
        if not resp.content:
            return {}
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def get(self, path: str, params: dict | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, json: dict | None = None) -> Any:
        return self._request("POST", path, json=json)


def from_session() -> PPClient:
    return PPClient(token=session.current_token())
