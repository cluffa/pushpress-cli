import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"

LOGIN_RESP = {
    "clientUuid": "client_1",
    "userUuid": "usr_1",
    "company": "Test Gym",
    "subdomain": "testgym",
    "accessToken": "eyJ.a.b",
    "tokenExpiration": "2999-01-01T00:00:00.000",
    "privileges": [],
}


@respx.mock
def test_login_stores_session(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    respx.post(f"{BASE}/v2/auth/login").mock(return_value=httpx.Response(200, json=LOGIN_RESP))
    result = runner.invoke(app, ["login", "--email", "a@b.com", "--password-stdin"], input="pw\n")
    assert result.exit_code == 0
    body = json.loads(result.stdout)
    assert body["clientUuid"] == "client_1"
    assert (tmp_path / "session.json").exists()


def test_whoami_without_session_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    monkeypatch.delenv("PP_TOKEN", raising=False)
    result = runner.invoke(app, ["whoami"])
    assert result.exit_code == 3
    assert json.loads(result.stderr)["code"] == "auth_required"
