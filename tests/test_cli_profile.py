from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


@respx.mock
def test_profile_command(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"profile": {"firstName": "Alex"}}})
    )
    result = runner.invoke(app, ["profile"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["profile"]["firstName"] == "Alex"


@respx.mock
def test_profile_heals_empty_stored_ids(tmp_path, monkeypatch):
    # A session stored before the login fix: valid token, empty UUIDs.
    # Profile must resolve the identity from the token, not query with "".
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "", "userUuid": "", "accessToken": "tok"
    }))
    respx.get(f"{BASE}/v2/auth/verify/tok").mock(
        return_value=httpx.Response(
            200,
            json={"isValid": True, "payload": {"clientUuid": "client_test_gym", "sub": "usr_test_member"}},
        )
    )
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"profile": {"firstName": "Test"}}})
    )
    result = runner.invoke(app, ["profile"])
    assert result.exit_code == 0
    variables = json.loads(route.calls.last.request.content)["variables"]
    assert variables == {"clientUuid": "client_test_gym", "userUuid": "usr_test_member"}
    # The healed IDs are persisted back to the session file.
    stored = json.loads((tmp_path / "session.json").read_text())
    assert stored["clientUuid"] == "client_test_gym"
    assert stored["userUuid"] == "usr_test_member"
