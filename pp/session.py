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


def clear() -> None:
    path = config.session_path()
    if path.exists():
        path.unlink()


def current_token() -> str:
    env = os.environ.get("PP_TOKEN")
    if env:
        return env
    return load().access_token
