from __future__ import annotations

import json

import httpx
import respx

from pp.api import workouts
from pp.http import PPClient

BASE = "https://api.pushpress.com"


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
