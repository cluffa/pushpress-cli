from __future__ import annotations

import json

import httpx
import pytest
import respx

from pp.api import reservations as reservationapi
from pp.errors import UpstreamError, UsageError
from pp.http import PPClient

BASE = "https://api.pushpress.com"


@respx.mock
def test_create_reservation_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"createReservation": {"uuid": "reg_1", "__typename": "Registration"}}})
    )
    result = reservationapi.create_reservation(PPClient(token="tok"), "cu_1", "cal-1", "sub_1")
    assert result["data"]["createReservation"]["uuid"] == "reg_1"


@respx.mock
def test_create_reservation_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    reservationapi.create_reservation(PPClient(token="tok"), "cu_1", "cal-1", "sub_1")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"] == {
        "clientUserUuid": "cu_1",
        "calendarItemUuid": "cal-1",
        "subscriptionUuid": "sub_1",
        "source": None,
    }
    assert "createReservation" in body["query"]
    assert "createReservationInput" in body["query"]


@respx.mock
def test_create_reservation_graphql_error_raises():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": None, "errors": [{"message": "Class is full"}]})
    )
    with pytest.raises(UpstreamError) as excinfo:
        reservationapi.create_reservation(PPClient(token="tok"), "cu_1", "cal-1", "sub_1")
    assert excinfo.value.detail == "Class is full"


@respx.mock
def test_cancel_reservation_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"cancelReservation": {"uuid": "reg_1", "__typename": "Registration"}}})
    )
    result = reservationapi.cancel_reservation(PPClient(token="tok"), "reg_1")
    assert result["data"]["cancelReservation"]["uuid"] == "reg_1"


@respx.mock
def test_cancel_reservation_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    reservationapi.cancel_reservation(PPClient(token="tok"), "reg_99")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"] == {"reservationId": "reg_99"}
    assert "cancelReservation" in body["query"]
    assert "cancelReservationInput" in body["query"]


@respx.mock
def test_cancel_reservation_graphql_error_raises():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": None, "errors": [{"message": "Reservation not found"}]})
    )
    with pytest.raises(UpstreamError):
        reservationapi.cancel_reservation(PPClient(token="tok"), "reg_nope")


@respx.mock
def test_checkin_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"checkin": {"uuid": "chk_1", "__typename": "Checkin"}}})
    )
    result = reservationapi.checkin_reservation(PPClient(token="tok"), "reg_1")
    assert result["data"]["checkin"]["uuid"] == "chk_1"


@respx.mock
def test_checkin_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    reservationapi.checkin_reservation(PPClient(token="tok"), "reg_99")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"] == {"reservationId": "reg_99", "source": None}
    assert "checkin" in body["query"]
    assert "checkinInput" in body["query"]


@respx.mock
def test_checkin_graphql_error_raises():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": None, "errors": [{"message": "Too early to check in"}]})
    )
    with pytest.raises(UpstreamError) as excinfo:
        reservationapi.checkin_reservation(PPClient(token="tok"), "reg_1")
    assert excinfo.value.detail == "Too early to check in"


_PROFILE = {
    "data": {
        "profile": {
            "clientUserUuid": "cu_1",
            "subscriptions": [
                {"subscriptionUuid": "sub_old", "status": "cancelled", "active": False},
                {"subscriptionUuid": "sub_1", "status": "active", "active": True},
            ],
        }
    }
}


@respx.mock
def test_booking_identity_resolves_active_subscription():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json=_PROFILE)
    )
    client_user_uuid, subscription_uuid = reservationapi.booking_identity(
        PPClient(token="tok"), "client_1", "usr_1"
    )
    assert client_user_uuid == "cu_1"
    assert subscription_uuid == "sub_1"


@respx.mock
def test_booking_identity_no_subscription_raises():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"profile": {"clientUserUuid": "cu_1", "subscriptions": []}}})
    )
    with pytest.raises(UsageError):
        reservationapi.booking_identity(PPClient(token="tok"), "client_1", "usr_1")


@respx.mock
def test_booking_identity_no_client_user_uuid_raises():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"profile": {"clientUserUuid": None, "subscriptions": []}}})
    )
    with pytest.raises(UpstreamError):
        reservationapi.booking_identity(PPClient(token="tok"), "client_1", "usr_1")
