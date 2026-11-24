import os
import stat

import httpx
import pytest
import respx

from pp import config, session
from pp.models import Session
from pp.errors import AuthError

BASE = "https://api.pushpress.com"

ACCESS_DATA = {
    "clientUuid": "client_1",
    "userUuid": "usr_1",
    "company": "Test Gym",
    "subdomain": "testgym",
    "accessToken": "eyJ.a.b",
    "tokenExpiration": "2999-01-01T00:00:00.000",
    "privileges": ["feed.activity.view"],
}


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    monkeypatch.delenv("PP_TOKEN", raising=False)
    return tmp_path


def test_from_access_data_and_roundtrip(tmp_config):
    sess = Session.from_access_data(ACCESS_DATA)
    assert sess.client_uuid == "client_1"
    assert sess.access_token == "eyJ.a.b"
    assert sess.is_expired is False
    session.save(sess)
    mode = stat.S_IMODE(os.stat(config.session_path()).st_mode)
    assert mode == 0o600
    assert session.load().user_uuid == "usr_1"


def test_expired():
    d = dict(ACCESS_DATA, tokenExpiration="2000-01-01T00:00:00.000")
    assert Session.from_access_data(d).is_expired is True


def test_load_missing_raises(tmp_config):
    with pytest.raises(AuthError):
        session.load()


def test_current_token_prefers_env(tmp_config, monkeypatch):
    monkeypatch.setenv("PP_TOKEN", "envtok")
    assert session.current_token() == "envtok"


def test_clear(tmp_config):
    session.save(Session.from_access_data(ACCESS_DATA))
    session.clear()
    with pytest.raises(AuthError):
        session.load()


@respx.mock
def test_resolve_heals_empty_ids_and_persists(tmp_config):
    session.save(Session.from_access_data(dict(ACCESS_DATA, clientUuid="", userUuid="")))
    respx.get(f"{BASE}/v2/auth/verify/eyJ.a.b").mock(
        return_value=httpx.Response(
            200,
            json={"isValid": True, "payload": {"clientUuid": "client_test_gym", "sub": "usr_test_member"}},
        )
    )
    healed = session.resolve()
    assert healed.client_uuid == "client_test_gym"
    assert healed.user_uuid == "usr_test_member"
    # Persisted: a fresh load sees the healed IDs.
    assert session.load().client_uuid == "client_test_gym"
    assert session.load().user_uuid == "usr_test_member"


@respx.mock
def test_resolve_skips_verify_when_ids_present(tmp_config):
    session.save(Session.from_access_data(ACCESS_DATA))
    route = respx.get(f"{BASE}/v2/auth/verify/eyJ.a.b").mock(
        return_value=httpx.Response(200, json={"isValid": True, "payload": {}})
    )
    sess = session.resolve()
    assert sess.client_uuid == "client_1"
    assert sess.user_uuid == "usr_1"
    assert not route.called


@respx.mock
def test_resolve_returns_stored_when_verify_fails(tmp_config):
    session.save(Session.from_access_data(dict(ACCESS_DATA, clientUuid="", userUuid="")))
    respx.get(f"{BASE}/v2/auth/verify/eyJ.a.b").mock(return_value=httpx.Response(401, json={}))
    sess = session.resolve()
    assert sess.client_uuid == ""
    assert sess.user_uuid == ""
