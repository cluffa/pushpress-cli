from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


@respx.mock
def test_preorders_command(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={
            "data": {
                "preorders": [
                    {
                        "uuid": "po_1",
                        "name": "Limited Tee",
                        "startTimestamp": "2026-08-01T00:00:00Z",
                        "endTimestamp": "2026-08-15T00:00:00Z",
                        "productImage": "https://example.com/tee.png",
                        "purchased": False,
                        "__typename": "Preorder",
                    }
                ],
                "__typename": "Query",
            }
        })
    )
    result = runner.invoke(app, ["preorders"])
    assert result.exit_code == 0
    body = json.loads(result.stdout)
    assert body["data"]["preorders"][0]["name"] == "Limited Tee"
