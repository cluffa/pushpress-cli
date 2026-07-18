from __future__ import annotations

import json

import httpx
import respx

from pp.api import events
from pp.http import PPClient

BASE = "https://api.pushpress.com"


@respx.mock
def test_get_events_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={
            "data": {
                "events": [
                    {
                        "uuid": "evt_1",
                        "title": "Summer Party",
                        "price": 0,
                        "isAllDay": False,
                        "startTime": "2026-08-01T18:00:00Z",
                        "endTime": "2026-08-01T22:00:00Z",
                        "registrations": [],
                        "__typename": "CalendarItem",
                    }
                ],
                "__typename": "Query",
            }
        })
    )
    result = events.get_events(PPClient(token="tok"), "2026-08-01", "2026-08-31")
    assert result["data"]["events"][0]["title"] == "Summer Party"


@respx.mock
def test_get_events_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"events": []}})
    )
    events.get_events(PPClient(token="tok"), "2026-07-01", "2027-01-01")
    body = json.loads(route.calls.last.request.content)
    assert body["query"]
    assert body["variables"]["startDate"] == "2026-07-01"
    assert body["variables"]["endDate"] == "2027-01-01"
