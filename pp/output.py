from __future__ import annotations

import functools
import json
import sys

import typer

from pp.errors import PPError


def select_fields(obj, fields):
    if not fields:
        return obj
    if isinstance(obj, dict):
        return {k: obj[k] for k in fields if k in obj}
    if isinstance(obj, list):
        return [select_fields(x, fields) for x in obj]
    return obj


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
