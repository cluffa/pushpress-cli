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


LOGIN_RESP_NESTED = {
    "clients": [
        {
            "clientId": 10001,
            "clientUuid": "client_test_gym",
            "company": "Test Gym",
            "subdomain": "testgym",
            "role": "member",
            "active": True,
            "userUuid": "usr_test_member",
            "accessToken": "eyJ.a.b",
        }
    ],
    "features": {},
    "accessToken": "eyJ.a.b",
    "refreshToken": "eyJ.a.b",
    "profileUuid": "profile_test_1",
}


@respx.mock
def test_login_stores_ids_from_nested_response(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    respx.post(f"{BASE}/v2/auth/login").mock(return_value=httpx.Response(200, json=LOGIN_RESP_NESTED))
    respx.get(f"{BASE}/v2/auth/verify/eyJ.a.b").mock(
        return_value=httpx.Response(
            200,
            json={"isValid": True, "payload": {"clientUuid": "client_test_gym", "sub": "usr_test_member", "exp": 4102444800}},
        )
    )
    result = runner.invoke(app, ["login", "--email", "a@b.com", "--password-stdin"], input="pw\n")
    assert result.exit_code == 0
    body = json.loads(result.stdout)
    assert body["clientUuid"] == "client_test_gym"
    assert body["userUuid"] == "usr_test_member"
    stored = json.loads((tmp_path / "session.json").read_text())
    assert stored["clientUuid"] == "client_test_gym"
    assert stored["userUuid"] == "usr_test_member"


def test_whoami_without_session_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    monkeypatch.delenv("PP_TOKEN", raising=False)
    result = runner.invoke(app, ["whoami"])
    assert result.exit_code == 3
    assert json.loads(result.stderr)["code"] == "auth_required"
