from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


@respx.mock
def test_events_command(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
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
    result = runner.invoke(app, ["events", "--start-date", "2026-08-01", "--end-date", "2026-08-31"])
    assert result.exit_code == 0
    body = json.loads(result.stdout)
    assert body["data"]["events"][0]["title"] == "Summer Party"
