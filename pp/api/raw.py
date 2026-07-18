from __future__ import annotations

from typing import Any

from pp.http import PPClient


def get(c: PPClient, path: str, params: dict | None = None) -> Any:
    return c.get(path, params=params)
