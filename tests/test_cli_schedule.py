from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


@respx.mock
def test_schedule_list_command(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"classes": [{"title": "Yoga"}]}})
    )
    result = runner.invoke(app, ["schedule", "--date", "2026-07-17"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["classes"][0]["title"] == "Yoga"


@respx.mock
def test_schedule_detail_command(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"getClass": {"title": "Yoga"}}})
    )
    result = runner.invoke(app, ["schedule", "--class-id", "cal-abc"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["getClass"]["title"] == "Yoga"
