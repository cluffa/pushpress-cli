from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


@respx.mock
def test_workouts_types_list(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"workoutTypes": [{"name": "CrossFit"}]}})
    )
    result = runner.invoke(app, ["workouts", "--date", "2026-07-17"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["workoutTypes"][0]["name"] == "CrossFit"


@respx.mock
def test_workouts_wod(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"workoutOfDay": {"title": "Fran"}}})
    )
    result = runner.invoke(app, ["workouts", "--date", "2026-07-17", "--type-id", "type-1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["workoutOfDay"]["title"] == "Fran"


@respx.mock
def test_workouts_part_detail(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"workoutPart": {"title": "Part 1"}}})
    )
    result = runner.invoke(app, ["workouts", "--part-id", "part-1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["workoutPart"]["title"] == "Part 1"


@respx.mock
def test_workouts_score_history(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"scoreHistory": [{"title": "Fran"}]}})
    )
    result = runner.invoke(app, ["workouts", "--keyword", "fran"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["scoreHistory"][0]["title"] == "Fran"


# ── wod ──────────────────────────────────────────────────────────────────────


def _wod_mock_handler(types, wod_per_type):
    """Build a side-effect handler for wod tests.

    types: list of {"name": str, "uid": str}
    wod_per_type: dict mapping uid -> WOD response data or None for empty
    """

    def handler(request):
        import json as _j
        body = _j.loads(request.content)
        if "getClassTypes" in body["query"]:
            return httpx.Response(200, json={
                "data": {
                    "workoutTypes": [
                        {"name": t["name"], "uid": t["uid"], "origin": None,
                         "static": False, "progressiveProgram": None, "lastDayNum": None,
                         "__typename": "ClassType"}
                        for t in types
                    ],
                    "__typename": "Query",
                }
            })
        ct_id = body.get("variables", {}).get("classTypeId")
        wod = wod_per_type.get(ct_id)
        if wod:
            return httpx.Response(200, json={
                "data": {"workoutOfDay": [wod], "__typename": "Query"}
            })
        return httpx.Response(200, json={
            "data": {"workoutOfDay": [], "__typename": "Query"}
        })

    return handler


@respx.mock
def test_wod_command_auto_discovers(tmp_path, monkeypatch):
    """pp wod should auto-discover the correct class type."""
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(side_effect=_wod_mock_handler(
        types=[{"name": "CrossFit", "uid": "ct-1"}],
        wod_per_type={
            "ct-1": {
                "uid": "wod-1", "title": "Today's WOD", "workoutState": "PUBLISHED",
                "parts": [
                    {"workoutPartUid": "p1", "title": "Metcon",
                     "description": "AMRAP 10", "scoreType": "Rounds/Reps",
                     "__typename": "WorkoutOfDayParts"},
                ],
                "__typename": "WorkoutOfDay",
            }
        },
    ))
    result = runner.invoke(app, ["wod", "--date", "2026-07-20"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["class_type_name"] == "CrossFit"
    assert data["workout"]["title"] == "Today's WOD"


@respx.mock
def test_wod_command_no_wod(tmp_path, monkeypatch):
    """pp wod should return null workout when no WOD exists."""
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(side_effect=_wod_mock_handler(
        types=[{"name": "CrossFit", "uid": "ct-1"}],
        wod_per_type={"ct-1": None},
    ))
    result = runner.invoke(app, ["wod", "--date", "2026-07-20"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["workout"] is None


@respx.mock
def test_wod_tomorrow_flag(tmp_path, monkeypatch):
    """pp wod --tomorrow should work and pass a future date."""
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    calls = []

    def handler(request):
        import json as _j
        body = _j.loads(request.content)
        calls.append(body)
        if "getClassTypes" in body["query"]:
            return httpx.Response(200, json={
                "data": {"workoutTypes": [], "__typename": "Query"}
            })
        return httpx.Response(200, json={"data": {}})

    respx.post(f"{BASE}/v2/graph/graphql").mock(side_effect=handler)
    result = runner.invoke(app, ["wod", "--tomorrow"])
    assert result.exit_code == 0
    types_call = next((c for c in calls if "getClassTypes" in c["query"]), None)
    assert types_call is not None
    from datetime import date as dt, timedelta
    expected = (dt.today() + timedelta(days=1)).isoformat()
    assert types_call["variables"]["classDate"] == expected


@respx.mock
def test_wod_yesterday_flag(tmp_path, monkeypatch):
    """pp wod --yesterday should work and pass a past date."""
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    calls = []

    def handler(request):
        import json as _j
        body = _j.loads(request.content)
        calls.append(body)
        if "getClassTypes" in body["query"]:
            return httpx.Response(200, json={
                "data": {"workoutTypes": [], "__typename": "Query"}
            })
        return httpx.Response(200, json={"data": {}})

    respx.post(f"{BASE}/v2/graph/graphql").mock(side_effect=handler)
    result = runner.invoke(app, ["wod", "--yesterday"])
    assert result.exit_code == 0
    types_call = next((c for c in calls if "getClassTypes" in c["query"]), None)
    assert types_call is not None
    from datetime import date as dt, timedelta
    expected = (dt.today() - timedelta(days=1)).isoformat()
    assert types_call["variables"]["classDate"] == expected


@respx.mock
def test_wod_command_no_types(tmp_path, monkeypatch):
    """pp wod should return null workout when no class types."""
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={
            "data": {"workoutTypes": [], "__typename": "Query"}
        })
    )
    result = runner.invoke(app, ["wod", "--date", "2026-07-20"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["workout"] is None
