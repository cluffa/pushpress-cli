from __future__ import annotations

import json

import httpx
import respx

from pp.api import profile
from pp.http import PPClient

BASE = "https://api.pushpress.com"


@respx.mock
def test_get_profile_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"profile": {"firstName": "Alex"}}})
    )
    result = profile.get_profile(PPClient(token="tok"), "client_1", "usr_1")
    assert result["data"]["profile"]["firstName"] == "Alex"


@respx.mock
def test_get_profile_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    profile.get_profile(PPClient(token="tok"), "client_9", "usr_9")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["clientUuid"] == "client_9"
    assert body["variables"]["userUuid"] == "usr_9"
