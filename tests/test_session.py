import os
import stat

import pytest

from pp import config, session
from pp.models import Session
from pp.errors import AuthError

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
