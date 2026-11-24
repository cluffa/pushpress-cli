from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


def _session(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))


@respx.mock
def test_reserve_creates_reservation(tmp_path, monkeypatch):
    _session(tmp_path, monkeypatch)
    respx.post(f"{BASE}/v2/graph/graphql").mock(side_effect=[
        httpx.Response(200, json={"data": {"profile": {
            "clientUserUuid": "cu_1",
            "subscriptions": [{"subscriptionUuid": "sub_1", "status": "active", "active": True}],
        }}}),
        httpx.Response(200, json={"data": {"createReservation": {"uuid": "reg_1", "__typename": "Registration"}}}),
    ])
    result = runner.invoke(app, ["reserve", "--class-id", "cal-1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["createReservation"]["uuid"] == "reg_1"


@respx.mock
def test_reserve_api_rejection_exits_nonzero(tmp_path, monkeypatch):
    _session(tmp_path, monkeypatch)
    respx.post(f"{BASE}/v2/graph/graphql").mock(side_effect=[
        httpx.Response(200, json={"data": {"profile": {
            "clientUserUuid": "cu_1",
            "subscriptions": [{"subscriptionUuid": "sub_1", "status": "active", "active": True}],
        }}}),
        httpx.Response(200, json={"data": None, "errors": [{"message": "Class is full"}]}),
    ])
    result = runner.invoke(app, ["reserve", "--class-id", "cal-1"])
    assert result.exit_code == 5
    assert "Class is full" in result.stderr


@respx.mock
def test_cancel_reservation(tmp_path, monkeypatch):
    _session(tmp_path, monkeypatch)
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"cancelReservation": {"uuid": "reg_1", "__typename": "Registration"}}})
    )
    result = runner.invoke(app, ["cancel-reservation", "--reservation-id", "reg_1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["cancelReservation"]["uuid"] == "reg_1"


@respx.mock
def test_checkin(tmp_path, monkeypatch):
    _session(tmp_path, monkeypatch)
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"checkin": {"uuid": "chk_1", "__typename": "Checkin"}}})
    )
    result = runner.invoke(app, ["checkin", "--reservation-id", "reg_1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["checkin"]["uuid"] == "chk_1"


@respx.mock
def test_checkin_api_rejection_exits_nonzero(tmp_path, monkeypatch):
    _session(tmp_path, monkeypatch)
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": None, "errors": [{"message": "Too early to check in"}]})
    )
    result = runner.invoke(app, ["checkin", "--reservation-id", "reg_1"])
    assert result.exit_code == 5
    assert "Too early to check in" in result.stderr
