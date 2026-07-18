import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


@respx.mock
def test_gym_uses_session_client_uuid(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("PP_TOKEN", "tok")
    (tmp_path / "session.json").write_text(json.dumps({"clientUuid": "client_9", "accessToken": "x"}))
    respx.get(f"{BASE}/v2/client/client/client_9").mock(
        return_value=httpx.Response(200, json={"company": "Nine"})
    )
    result = runner.invoke(app, ["gym"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["company"] == "Nine"


@respx.mock
def test_features_fields_projection(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("PP_TOKEN", "tok")
    (tmp_path / "session.json").write_text(json.dumps({"clientUuid": "client_9", "accessToken": "x"}))
    respx.get(f"{BASE}/v2/client/client/client_9/features").mock(
        return_value=httpx.Response(200, json={"appointments": True, "calendarV2": False})
    )
    result = runner.invoke(app, ["--fields", "appointments", "features"])
    assert json.loads(result.stdout) == {"appointments": True}
