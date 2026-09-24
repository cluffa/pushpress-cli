from __future__ import annotations

import json

import httpx
import respx

from pp.api import workouts
from pp.http import PPClient

BASE = "https://api.pushpress.com"

# ── workout_types ────────────────────────────────────────────────────────────


@respx.mock
def test_workout_types_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"workoutTypes": [{"name": "CrossFit"}]}})
    )
    result = workouts.workout_types(PPClient(token="tok"), "2026-07-17")
    assert result["data"]["workoutTypes"][0]["name"] == "CrossFit"


@respx.mock
def test_workout_types_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    workouts.workout_types(PPClient(token="tok"), "2026-07-17")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["classDate"] == "2026-07-17"


@respx.mock
def test_workout_types_no_unused_fragments():
    """Verify the query has no fragment definitions (getClassTypes needs none)."""
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    workouts.workout_types(PPClient(token="tok"), "2026-07-17")
    body = json.loads(route.calls.last.request.content)
    query = body["query"]
    # Should NOT define any fragments
    assert "fragment " not in query, "workout_types query should have no fragments"


# ── workout_of_day ───────────────────────────────────────────────────────────


@respx.mock
def test_workout_of_day_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"workoutOfDay": {"title": "Fran"}}})
    )
    result = workouts.workout_of_day(PPClient(token="tok"), "2026-07-17", "type-1")
    assert result["data"]["workoutOfDay"]["title"] == "Fran"


@respx.mock
def test_workout_of_day_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    workouts.workout_of_day(PPClient(token="tok"), "2026-07-17", "type-1")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["classDate"] == "2026-07-17"
    assert body["variables"]["classTypeId"] == "type-1"


# ── workout_part ─────────────────────────────────────────────────────────────


@respx.mock
def test_workout_part_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"workoutPart": {"title": "Part 1"}}})
    )
    result = workouts.workout_part(PPClient(token="tok"), "part-1", workout_uid="wu-1", score_id=42)
    assert result["data"]["workoutPart"]["title"] == "Part 1"


@respx.mock
def test_workout_part_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    workouts.workout_part(PPClient(token="tok"), "part-1", workout_uid="wu-1", score_id=42)
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["workoutPartId"] == "part-1"
    assert body["variables"]["workoutUid"] == "wu-1"
    assert body["variables"]["scoreId"] == 42


# ── workout_scores ───────────────────────────────────────────────────────────


@respx.mock
def test_workout_scores_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"workoutGetScores": {"scores": [{"id": 1}]}}})
    )
    result = workouts.workout_scores(PPClient(token="tok"), "part-1", "2026-07-17", workout_uid="wu-1", class_type_id=91058.0)
    assert result["data"]["workoutGetScores"]["scores"][0]["id"] == 1


@respx.mock
def test_workout_scores_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    workouts.workout_scores(PPClient(token="tok"), "part-1", "2026-07-17", workout_uid="wu-1", class_type_id=91058.0)
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["workoutPartUid"] == "part-1"
    assert body["variables"]["date"] == "2026-07-17"
    assert body["variables"]["workoutUid"] == "wu-1"
    assert body["variables"]["classTypeId"] == 91058.0


@respx.mock
def test_workout_scores_no_unused_fragments():
    """Verify scores query only defines fragments it uses (no WorkoutOfDay)."""
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    workouts.workout_scores(PPClient(token="tok"), "part-1", "2026-07-17")
    body = json.loads(route.calls.last.request.content)
    query = body["query"]
    # Should define WorkoutScore but NOT WorkoutOfDay or WorkoutOfDayPart
    assert "fragment WorkoutScore" in query
    assert "fragment WorkoutOfDay" not in query, "scores query should not include WorkoutOfDay fragment"
    assert "fragment WorkoutOfDayPart" not in query


# ── score_history ────────────────────────────────────────────────────────────


@respx.mock
def test_score_history_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"scoreHistory": [{"title": "Fran"}]}})
    )
    result = workouts.score_history(PPClient(token="tok"), "fran")
    assert result["data"]["scoreHistory"][0]["title"] == "Fran"


@respx.mock
def test_score_history_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    workouts.score_history(PPClient(token="tok"), "fran")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["keyword"] == "fran"


@respx.mock
def test_score_history_no_fragments():
    """Verify score_history query has no fragment definitions."""
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    workouts.score_history(PPClient(token="tok"), "fran")
    body = json.loads(route.calls.last.request.content)
    query = body["query"]
    assert "fragment " not in query, "score_history query should have no fragments"


# ── wod_auto ─────────────────────────────────────────────────────────────────


@respx.mock
def test_wod_auto_finds_first_matching_type():
    """wod_auto should try class types and return the one with a WOD."""
    # First call: getClassTypes returns two types
    # Second call: first type returns empty WOD
    # Third call: second type returns a WOD
    calls = []

    def handler(request):
        body = json.loads(request.content)
        calls.append(body["query"])
        if "getClassTypes" in body["query"]:
            return httpx.Response(200, json={
                "data": {
                    "workoutTypes": [
                        {"name": "Empty Type", "uid": "ct-empty", "origin": None,
                         "static": False, "progressiveProgram": None, "lastDayNum": None,
                         "__typename": "ClassType"},
                        {"name": "CrossFit", "uid": "ct-crossfit", "origin": None,
                         "static": False, "progressiveProgram": None, "lastDayNum": None,
                         "__typename": "ClassType"},
                    ],
                    "__typename": "Query",
                }
            })
        # getWorkoutOfDay call
        variables = body.get("variables", {})
        if variables.get("classTypeId") == "ct-empty":
            return httpx.Response(200, json={
                "data": {"workoutOfDay": [], "__typename": "Query"}
            })
        if variables.get("classTypeId") == "ct-crossfit":
            return httpx.Response(200, json={
                "data": {
                    "workoutOfDay": [{
                        "uid": "wod-1", "title": "Today's WOD", "workoutState": "PUBLISHED",
                        "parts": [
                            {"workoutPartUid": "p1", "title": "Warm-up",
                             "description": "Dynamic warm-up", "scoreType": "No Score",
                             "__typename": "WorkoutOfDayParts"},
                            {"workoutPartUid": "p2", "title": "Metcon",
                             "description": "AMRAP 10", "scoreType": "Rounds/Reps",
                             "__typename": "WorkoutOfDayParts"},
                        ],
                        "__typename": "WorkoutOfDay",
                    }],
                    "__typename": "Query",
                }
            })
        return httpx.Response(200, json={"data": {}})

    respx.post(f"{BASE}/v2/graph/graphql").mock(side_effect=handler)

    result = workouts.wod_auto(PPClient(token="tok"), "2026-07-20")
    assert result["class_type_name"] == "CrossFit"
    assert result["class_type_uid"] == "ct-crossfit"
    assert result["workout"] is not None
    assert result["workout"]["title"] == "Today's WOD"
    assert result["date"] == "2026-07-20"
    # Should have tried exactly 2 types (empty first, then crossfit)
    assert len([c for c in calls if "getWorkoutOfDay" in c]) == 2


@respx.mock
def test_wod_auto_no_matching_type():
    """wod_auto returns None workout when no class type has a WOD."""
    def handler(request):
        body = json.loads(request.content)
        if "getClassTypes" in body["query"]:
            return httpx.Response(200, json={
                "data": {
                    "workoutTypes": [
                        {"name": "Type A", "uid": "ct-a", "origin": None,
                         "static": False, "progressiveProgram": None, "lastDayNum": None,
                         "__typename": "ClassType"},
                    ],
                    "__typename": "Query",
                }
            })
        return httpx.Response(200, json={
            "data": {"workoutOfDay": [], "__typename": "Query"}
        })

    respx.post(f"{BASE}/v2/graph/graphql").mock(side_effect=handler)
    result = workouts.wod_auto(PPClient(token="tok"), "2026-07-20")
    assert result["workout"] is None
    assert result["date"] == "2026-07-20"


@respx.mock
def test_wod_auto_no_types():
    """wod_auto returns None workout when no class types exist."""
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={
            "data": {"workoutTypes": [], "__typename": "Query"}
        })
    )
    result = workouts.wod_auto(PPClient(token="tok"), "2026-07-20")
    assert result["workout"] is None
    assert result["date"] == "2026-07-20"
