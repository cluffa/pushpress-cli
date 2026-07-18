from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


@respx.mock
def test_appointments_default_upcoming(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"reservations": [{"id": "r-1", "reservationTitle": "Yoga"}]}})
    )
    result = runner.invoke(app, ["appointments"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["reservations"][0]["reservationTitle"] == "Yoga"


@respx.mock
def test_appointments_types(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"types": [{"uuid": "at-1", "name": "Private Training"}]}})
    )
    result = runner.invoke(app, ["appointments", "--types"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["types"][0]["name"] == "Private Training"


@respx.mock
def test_appointments_packages(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"packages": [{"uuid": "pkg-1", "name": "10 Pack"}]}})
    )
    result = runner.invoke(app, ["appointments", "--packages"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["packages"][0]["name"] == "10 Pack"


@respx.mock
def test_appointments_credits(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"counts": [{"appointmentTypeUuid": "at-1", "count": 5}]}})
    )
    result = runner.invoke(app, ["appointments", "--credits"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["counts"][0]["count"] == 5


@respx.mock
def test_appointments_history(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"history": [{"uuid": "ah-1", "eventStatus": "COMPLETED"}]}})
    )
    result = runner.invoke(app, ["appointments", "--history"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["history"][0]["eventStatus"] == "COMPLETED"
