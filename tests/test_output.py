import json

from pp.output import emit, emit_error, select_fields
from pp.errors import AuthError


def test_select_fields_dict():
    assert select_fields({"a": 1, "b": 2, "c": 3}, ["a", "c"]) == {"a": 1, "c": 3}


def test_select_fields_list():
    got = select_fields([{"a": 1, "b": 2}, {"a": 3, "b": 4}], ["a"])
    assert got == [{"a": 1}, {"a": 3}]


def test_emit_json_default(capsys):
    emit({"x": 1})
    out = capsys.readouterr().out
    assert json.loads(out) == {"x": 1}


def test_emit_ndjson(capsys):
    emit([{"a": 1}, {"a": 2}], ndjson=True)
    lines = capsys.readouterr().out.strip().splitlines()
    assert [json.loads(l) for l in lines] == [{"a": 1}, {"a": 2}]


def test_emit_error_to_stderr(capsys):
    emit_error(AuthError("no token"))
    cap = capsys.readouterr()
    assert cap.out == ""
    assert json.loads(cap.err) == {"error": "no token", "code": "auth_required"}
