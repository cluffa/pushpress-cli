from __future__ import annotations

import os
import pathlib


def config_dir() -> pathlib.Path:
    override = os.environ.get("PP_CONFIG_DIR")
    if override:
        d = pathlib.Path(override)
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        base = pathlib.Path(xdg) if xdg else pathlib.Path.home() / ".config"
        d = base / "pp"
    d.mkdir(parents=True, exist_ok=True, mode=0o700)
    return d


def session_path() -> pathlib.Path:
    return config_dir() / "session.json"
