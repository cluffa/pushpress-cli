from __future__ import annotations

import functools
import json
import sys

import typer

from pp.errors import PPError, UsageError

_MISSING = object()


def _get_path(obj, path):
    """Resolve a dotted path (e.g. "location.name", "scores.primaryScore").

    Path segments map over lists, so "scores.primaryScore" collects that key
    from every item in ``scores``.
    """
    return _resolve(obj, path.split("."))


def _resolve(cur, parts):
    if not parts:
        return cur
    part, rest = parts[0], parts[1:]
    if isinstance(cur, dict):
        if part not in cur:
            return _MISSING
        return _resolve(cur[part], rest)
    if isinstance(cur, list):
        out = []
        for item in cur:
            v = _resolve(item, parts)
            if v is not _MISSING:
                out.append(v)
        return out if out else _MISSING
    return _MISSING


def _has_any(obj, fields) -> bool:
    if isinstance(obj, list):
        return any(_has_any(x, fields) for x in obj)
    if isinstance(obj, dict):
        return any(_get_path(obj, f) is not _MISSING for f in fields)
    return False


def _unwrap(obj):
    """Strip a GraphQL envelope: {"data": {"<alias>": payload}} -> payload.

    When ``data`` holds several aliases, the ``data`` dict itself is returned.
    A null ``data`` unwraps to None.
    """
    if isinstance(obj, dict) and "data" in obj:
        inner = obj["data"]
        if inner is None:
            return None
        if isinstance(inner, dict):
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
    works on ``{"data": {"profile": {...}}}``. Raises UsageError when any
    requested field is unknown. GraphQL error payloads
    (``{"data": null, "errors": [...]}``) and null payloads pass through
    unchanged instead of being masked by a usage error.
    """
    if not fields:
        return obj
    if not isinstance(obj, (dict, list)):
        return obj
    if isinstance(obj, dict) and obj.get("errors") and not isinstance(obj.get("data"), dict):
        # Upstream GraphQL error: don't let field selection hide it.
        return obj
    target = obj if _has_any(obj, fields) else _unwrap(obj)
    if target is None:
        return None
    if target == []:
        return []
    missing = [f for f in fields if not _has_any(target, [f])]
    if missing:
        raise UsageError(
            f"unknown field(s): {', '.join(missing)}",
            detail=f"available fields: {', '.join(_available_keys(target))}",
            hint="use dotted paths for nested keys, e.g. --fields location.name",
        )
    return _project(target, fields)


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
