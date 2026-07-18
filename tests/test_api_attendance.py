from __future__ import annotations

import json

import httpx
import respx

from pp.api import attendance
from pp.http import PPClient

BASE = "https://api.pushpress.com"


@respx.mock
def test_get_attendance_stats_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={
            "data": {
                "getAttendanceStats": {
                    "week": 3, "month": 12, "year": 100, "allTime": 500,
                    "__typename": "AttendanceStats",
                }
            }
        })
    )
    result = attendance.get_attendance_stats(PPClient(token="tok"), "client_1", "usr_1")
    assert result["data"]["getAttendanceStats"]["week"] == 3
    assert result["data"]["getAttendanceStats"]["allTime"] == 500


@respx.mock
def test_get_attendance_stats_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    attendance.get_attendance_stats(PPClient(token="tok"), "client_9", "usr_9")
    body = json.loads(route.calls.last.request.content)
    assert body["query"]
    assert body["variables"]["clientUuid"] == "client_9"
    assert body["variables"]["userUuid"] == "usr_9"
