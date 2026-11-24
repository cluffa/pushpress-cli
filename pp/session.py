from __future__ import annotations

import json
import os

from pp import config
from pp.errors import AuthError
from pp.models import Session


def save(sess: Session) -> None:
    path = config.session_path()
    path.write_text(json.dumps(sess.to_dict(), indent=2))
    os.chmod(path, 0o600)


def load() -> Session:
    path = config.session_path()
    if not path.exists():
        raise AuthError("not logged in", hint="run: pp login")
    return Session.from_access_data(json.loads(path.read_text()))


def resolve() -> Session:
    """Load the session, healing empty identity fields from the token.

    Sessions stored before the login fix may hold a valid token but empty
    client/user UUIDs; commands that read the stored UUIDs directly then
    query the API with an empty identity. Resolve missing UUIDs from the
    token verify endpoint and persist the healed session so later loads
    are complete. Healing is best-effort: when verify is unavailable the
    stored session is returned unchanged.
    """
    sess = load()
    if sess.client_uuid and sess.user_uuid:
        return sess
    # Imported lazily: pp.http imports this module.
    from pp.api import auth
    from pp.errors import PPError
    from pp.http import PPClient

    try:
        result = auth.verify(PPClient(token=sess.access_token), sess.access_token)
    except PPError:
        return sess
    payload = result.get("payload", {}) if isinstance(result, dict) else {}
    if not isinstance(payload, dict):
        return sess
    changed = False
    if not sess.client_uuid and payload.get("clientUuid"):
        sess.client_uuid = payload["clientUuid"]
        changed = True
    user_uuid = payload.get("userUuid") or payload.get("sub")
    if not sess.user_uuid and user_uuid:
        sess.user_uuid = user_uuid
        changed = True
    if changed:
        save(sess)
    return sess


def clear() -> None:
    path = config.session_path()
    if path.exists():
        path.unlink()


def current_token() -> str:
    env = os.environ.get("PP_TOKEN")
    if env:
        return env
    return load().access_token
