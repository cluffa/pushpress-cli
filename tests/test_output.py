import json

import pytest

from pp.output import emit, emit_error, select_fields
from pp.errors import AuthError, UsageError


def test_select_fields_dict():
    assert select_fields({"a": 1, "b": 2, "c": 3}, ["a", "c"]) == {"a": 1, "c": 3}


def test_select_fields_list():
    got = select_fields([{"a": 1, "b": 2}, {"a": 3, "b": 4}], ["a"])
    assert got == [{"a": 1}, {"a": 3}]


def test_select_fields_unwraps_graphql_envelope():
    resp = {"data": {"profile": {"firstName": "A", "lastName": "B", "email": "x"}, "__typename": "Query"}}
    assert select_fields(resp, ["firstName", "lastName"]) == {"firstName": "A", "lastName": "B"}


def test_select_fields_unwraps_graphql_list():
    resp = {"data": {"classes": [{"title": "CF", "uuid": "1"}, {"title": "Oly", "uuid": "2"}]}}
    assert select_fields(resp, ["title"]) == [{"title": "CF"}, {"title": "Oly"}]


def test_select_fields_dotted_path():
    obj = {"location": {"name": "Main"}, "title": "CF"}
    assert select_fields(obj, ["location.name"]) == {"location.name": "Main"}


def test_select_fields_empty_graphql_list():
    assert select_fields({"data": {"classes": []}}, ["title"]) == []


def test_select_fields_missing_raises():
    with pytest.raises(UsageError) as ei:
        select_fields({"data": {"profile": {"firstName": "A"}}}, ["nope"])
    assert "firstName" in ei.value.detail


def test_select_fields_partial_unknown_raises():
    # Unknown fields are an error even when other fields match (per README).
    with pytest.raises(UsageError) as ei:
        select_fields({"a": 1, "b": 2}, ["a", "typo"])
    assert "typo" in str(ei.value)


def test_select_fields_graphql_errors_pass_through():
    # An upstream GraphQL error payload must not be masked by a usage error.
    payload = {"data": None, "errors": [{"message": "Fragment X is never used"}]}
    assert select_fields(payload, ["title"]) == payload


def test_select_fields_null_payload_returns_none():
    assert select_fields({"data": {"workoutOfDay": None}}, ["title"]) is None
    assert select_fields({"data": None}, ["title"]) is None


def test_select_fields_dotted_path_through_list():
    obj = {"data": {"workoutGetScores": {"scores": [{"primaryScore": 5}, {"primaryScore": 3}]}}}
    assert select_fields(obj, ["scores.primaryScore"]) == {"scores.primaryScore": [5, 3]}


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
