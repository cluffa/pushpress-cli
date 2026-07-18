from __future__ import annotations

import json

import httpx
import respx

from pp.api import preorders
from pp.http import PPClient

BASE = "https://api.pushpress.com"


@respx.mock
def test_get_preorders_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={
            "data": {
                "preorders": [
                    {
                        "uuid": "po_1",
                        "name": "Limited Tee",
                        "startTimestamp": "2026-08-01T00:00:00Z",
                        "endTimestamp": "2026-08-15T00:00:00Z",
                        "productImage": "https://example.com/tee.png",
                        "purchased": False,
                        "__typename": "Preorder",
                    }
                ],
                "__typename": "Query",
            }
        })
    )
    result = preorders.get_preorders(PPClient(token="tok"), "usr_1")
    assert result["data"]["preorders"][0]["name"] == "Limited Tee"


@respx.mock
def test_get_preorders_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"preorders": []}})
    )
    preorders.get_preorders(PPClient(token="tok"), "usr_9")
    body = json.loads(route.calls.last.request.content)
    assert body["query"]
    assert body["variables"]["userUuid"] == "usr_9"
