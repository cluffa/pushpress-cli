import httpx
import respx

from pp.api import auth
from pp.http import PPClient

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
def test_login_parses_session():
    respx.post(f"{BASE}/v2/auth/login").mock(return_value=httpx.Response(200, json=LOGIN_RESP))
    sess = auth.login("a@b.com", "pw")
    assert sess.client_uuid == "client_1"
    assert sess.access_token == "eyJ.a.b"


@respx.mock
def test_verify_returns_payload():
    respx.get(f"{BASE}/v2/auth/verify/tok").mock(
        return_value=httpx.Response(200, json={"isValid": True, "payload": {"sub": "usr_1"}})
    )
    out = auth.verify(PPClient(token="tok"), "tok")
    assert out["isValid"] is True
