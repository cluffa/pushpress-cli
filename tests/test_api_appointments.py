from __future__ import annotations

import json

import httpx
import respx

from pp.api import appointments as apptapi
from pp.http import PPClient

BASE = "https://api.pushpress.com"


@respx.mock
def test_appointment_types_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"types": [{"uuid": "at-1", "name": "Private Training"}]}})
    )
    result = apptapi.appointment_types(PPClient(token="tok"))
    assert result["data"]["types"][0]["name"] == "Private Training"


@respx.mock
def test_appointment_types_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    apptapi.appointment_types(PPClient(token="tok"))
    body = json.loads(route.calls.last.request.content)
    assert body["variables"] == {}


@respx.mock
def test_appointment_packages_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"packages": [{"uuid": "pkg-1", "name": "10 Pack"}]}})
    )
    result = apptapi.appointment_packages(PPClient(token="tok"))
    assert result["data"]["packages"][0]["name"] == "10 Pack"


@respx.mock
def test_appointment_packages_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    apptapi.appointment_packages(PPClient(token="tok"))
    body = json.loads(route.calls.last.request.content)
    assert body["variables"] == {}


@respx.mock
def test_appointment_credit_counts_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"counts": [{"appointmentTypeUuid": "at-1", "count": 5}]}})
    )
    result = apptapi.appointment_credit_counts(PPClient(token="tok"), "usr_1")
    assert result["data"]["counts"][0]["count"] == 5


@respx.mock
def test_appointment_credit_counts_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    apptapi.appointment_credit_counts(PPClient(token="tok"), "usr_99")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["userUuid"] == "usr_99"


@respx.mock
def test_appointment_history_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"history": [{"uuid": "ah-1", "eventStatus": "COMPLETED"}]}})
    )
    result = apptapi.appointment_history(PPClient(token="tok"), "usr_1")
    assert result["data"]["history"][0]["eventStatus"] == "COMPLETED"


@respx.mock
def test_appointment_history_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    apptapi.appointment_history(PPClient(token="tok"), "usr_99")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["userUuid"] == "usr_99"


@respx.mock
def test_upcoming_reservations_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"reservations": [{"id": "r-1", "reservationTitle": "Yoga"}]}})
    )
    result = apptapi.upcoming_reservations(PPClient(token="tok"))
    assert result["data"]["reservations"][0]["reservationTitle"] == "Yoga"


@respx.mock
def test_upcoming_reservations_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    apptapi.upcoming_reservations(PPClient(token="tok"))
    body = json.loads(route.calls.last.request.content)
    assert body["variables"] == {}
