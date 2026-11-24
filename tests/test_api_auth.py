import json

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
def test_login_sends_username_without_bearer():
    route = respx.post(f"{BASE}/v2/auth/login").mock(return_value=httpx.Response(200, json=LOGIN_RESP))
    auth.login("a@b.com", "pw")
    req = route.calls.last.request
    assert json.loads(req.content) == {"username": "a@b.com", "password": "pw"}
    assert "authorization" not in req.headers


def test_client_sends_bearer_when_token_present():
    assert PPClient(token="tok")._client.headers["Authorization"] == "Bearer tok"


# The live login response carries identity per gym under "clients"; only the
# token sits at the top level. All IDs below are fake placeholders.
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

VERIFY_RESP = {
    "isValid": True,
    "payload": {"clientUuid": "client_test_gym", "sub": "usr_test_member", "exp": 4102444800},
}


@respx.mock
def test_login_parses_nested_clients_response():
    respx.post(f"{BASE}/v2/auth/login").mock(return_value=httpx.Response(200, json=LOGIN_RESP_NESTED))
    respx.get(f"{BASE}/v2/auth/verify/eyJ.a.b").mock(return_value=httpx.Response(200, json=VERIFY_RESP))
    sess = auth.login("a@b.com", "pw")
    assert sess.client_uuid == "client_test_gym"
    assert sess.user_uuid == "usr_test_member"
    assert sess.company == "Test Gym"
    assert sess.subdomain == "testgym"
    assert sess.access_token == "eyJ.a.b"
    assert sess.token_expiration.startswith("2100-01-01")
    assert sess.is_expired is False


@respx.mock
def test_login_selects_client_matching_token():
    other = {
        "clientId": 10002,
        "clientUuid": "client_test_other",
        "company": "Other Gym",
        "subdomain": "othergym",
        "role": "member",
        "active": True,
        "userUuid": "usr_test_other",
        "accessToken": "eyJ.other.token",
    }
    resp = dict(LOGIN_RESP_NESTED, clients=[other, LOGIN_RESP_NESTED["clients"][0]])
    respx.post(f"{BASE}/v2/auth/login").mock(return_value=httpx.Response(200, json=resp))
    respx.get(f"{BASE}/v2/auth/verify/eyJ.a.b").mock(return_value=httpx.Response(200, json=VERIFY_RESP))
    sess = auth.login("a@b.com", "pw")
    assert sess.client_uuid == "client_test_gym"
    assert sess.company == "Test Gym"


@respx.mock
def test_login_nested_falls_back_when_verify_unavailable():
    respx.post(f"{BASE}/v2/auth/login").mock(return_value=httpx.Response(200, json=LOGIN_RESP_NESTED))
    respx.get(f"{BASE}/v2/auth/verify/eyJ.a.b").mock(return_value=httpx.Response(401, json={}))
    sess = auth.login("a@b.com", "pw")
    assert sess.client_uuid == "client_test_gym"
    assert sess.user_uuid == "usr_test_member"
    assert sess.company == "Test Gym"
    assert sess.token_expiration == ""


@respx.mock
def test_verify_returns_payload():
    respx.get(f"{BASE}/v2/auth/verify/tok").mock(
        return_value=httpx.Response(200, json={"isValid": True, "payload": {"sub": "usr_1"}})
    )
    out = auth.verify(PPClient(token="tok"), "tok")
    assert out["isValid"] is True
