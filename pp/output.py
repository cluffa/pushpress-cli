from __future__ import annotations

import functools
import json
import sys

import typer

from pp.errors import PPError, UsageError

_MISSING = object()


def _get_path(obj, path):
    """Resolve a dotted path (e.g. "location.name") inside a dict."""
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return _MISSING
    return cur


def _has_any(obj, fields) -> bool:
    if isinstance(obj, list):
        return any(_has_any(x, fields) for x in obj)
    if isinstance(obj, dict):
        return any(_get_path(obj, f) is not _MISSING for f in fields)
    return False


def _unwrap(obj):
    """Strip a GraphQL envelope: {"data": {"<alias>": payload}} -> payload.

    When ``data`` holds several aliases, the ``data`` dict itself is returned.
    """
    if isinstance(obj, dict) and isinstance(obj.get("data"), dict):
        inner = obj["data"]
        keys = [k for k in inner if k != "__typename"]
        if len(keys) == 1:
            return inner[keys[0]]
        return inner
    return obj


def _project(obj, fields):
    if isinstance(obj, list):
        return [_project(x, fields) for x in obj]
    if isinstance(obj, dict):
        out = {}
        for f in fields:
            v = _get_path(obj, f)
            if v is not _MISSING:
                out[f] = v
        return out
    return obj


def _available_keys(obj) -> list:
    if isinstance(obj, list):
        obj = next((x for x in obj if isinstance(x, dict)), {})
    return sorted(k for k in obj if k != "__typename") if isinstance(obj, dict) else []


def select_fields(obj, fields):
    """Project ``obj`` down to ``fields`` (top-level keys or dotted paths).

    GraphQL responses are unwrapped automatically, so ``--fields firstName``
    works on ``{"data": {"profile": {...}}}``. Raises UsageError instead of
    returning an empty result when none of the fields exist.
    """
    if not fields:
        return obj
    if not isinstance(obj, (dict, list)):
        return obj
    if _has_any(obj, fields):
        return _project(obj, fields)
    unwrapped = _unwrap(obj)
    if unwrapped == [] or obj == []:
        return []
    if _has_any(unwrapped, fields):
        return _project(unwrapped, fields)
    raise UsageError(
        f"none of the requested fields found: {', '.join(fields)}",
        detail=f"available fields: {', '.join(_available_keys(unwrapped))}",
        hint="use dotted paths for nested keys, e.g. --fields location.name",
    )


def emit(data, *, human=False, ndjson=False, fields=None, human_renderer=None):
    data = select_fields(data, fields)
    if ndjson and isinstance(data, list):
        for item in data:
            sys.stdout.write(json.dumps(item, default=str) + "\n")
        return
    if human and human_renderer is not None:
        human_renderer(data)
        return
    sys.stdout.write(json.dumps(data, indent=2, default=str) + "\n")


def emit_error(err: PPError) -> None:
    sys.stderr.write(json.dumps(err.to_dict(), default=str) + "\n")


def command(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except PPError as e:
            emit_error(e)
            raise typer.Exit(e.exit_code)

    return wrapper
