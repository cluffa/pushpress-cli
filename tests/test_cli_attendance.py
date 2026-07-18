from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


@respx.mock
def test_attendance_command(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
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
    result = runner.invoke(app, ["attendance"])
    assert result.exit_code == 0
    body = json.loads(result.stdout)
    assert body["data"]["getAttendanceStats"]["week"] == 3
    assert body["data"]["getAttendanceStats"]["allTime"] == 500
