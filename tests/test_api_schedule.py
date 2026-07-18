from __future__ import annotations

import json

import httpx
import respx

from pp.api import schedule
from pp.http import PPClient

BASE = "https://api.pushpress.com"


@respx.mock
def test_classes_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"classes": [{"title": "Yoga"}]}})
    )
    result = schedule.classes(PPClient(token="tok"), "2026-07-17")
    assert result["data"]["classes"][0]["title"] == "Yoga"


@respx.mock
def test_classes_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    schedule.classes(PPClient(token="tok"), "2026-07-17")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["classDate"] == "2026-07-17"


@respx.mock
def test_class_detail_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"getClass": {"title": "Yoga"}}})
    )
    result = schedule.class_detail(PPClient(token="tok"), "cal-abc")
    assert result["data"]["getClass"]["title"] == "Yoga"


@respx.mock
def test_class_detail_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    schedule.class_detail(PPClient(token="tok"), "cal-abc")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["classId"] == "cal-abc"
