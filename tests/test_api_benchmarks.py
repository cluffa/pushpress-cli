from __future__ import annotations

import json

import httpx
import respx

from pp.api import benchmarks
from pp.http import PPClient

BASE = "https://api.pushpress.com"


@respx.mock
def test_benchmark_types_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"benchmarkTypes": [{"key": "WEIGHTLIFTING", "displayName": "Weightlifting"}]}})
    )
    result = benchmarks.benchmark_types(PPClient(token="tok"))
    assert result["data"]["benchmarkTypes"][0]["key"] == "WEIGHTLIFTING"


@respx.mock
def test_benchmark_types_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    benchmarks.benchmark_types(PPClient(token="tok"))
    body = json.loads(route.calls.last.request.content)
    assert body["variables"] == {}


@respx.mock
def test_benchmark_workouts_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"benchmarks": [{"workoutUid": "wu-1", "title": "Fran"}]}})
    )
    result = benchmarks.benchmark_workouts(PPClient(token="tok"), benchmark_type="WEIGHTLIFTING", search="Fran")
    assert result["data"]["benchmarks"][0]["title"] == "Fran"


@respx.mock
def test_benchmark_workouts_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    benchmarks.benchmark_workouts(PPClient(token="tok"), benchmark_type="WEIGHTLIFTING", search="Fran")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["benchmarkType"] == "WEIGHTLIFTING"
    assert body["variables"]["searchString"] == "Fran"


@respx.mock
def test_benchmark_history_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"benchmarkWorkoutHistory": [{"workout": {"title": "Fran"}}]}})
    )
    result = benchmarks.benchmark_history(PPClient(token="tok"), "part-1")
    assert result["data"]["benchmarkWorkoutHistory"][0]["workout"]["title"] == "Fran"


@respx.mock
def test_benchmark_history_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    benchmarks.benchmark_history(PPClient(token="tok"), "part-1")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["workoutPartUid"] == "part-1"


@respx.mock
def test_weightlifting_history_returns_data():
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"weightliftingWorkoutHistory": [{"workout": {"title": "Clean"}}]}})
    )
    result = benchmarks.weightlifting_history(PPClient(token="tok"), "wu-1")
    assert result["data"]["weightliftingWorkoutHistory"][0]["workout"]["title"] == "Clean"


@respx.mock
def test_weightlifting_history_passes_variables():
    route = respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {}})
    )
    benchmarks.weightlifting_history(PPClient(token="tok"), "wu-1")
    body = json.loads(route.calls.last.request.content)
    assert body["variables"]["workoutUid"] == "wu-1"
