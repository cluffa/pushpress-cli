from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


@respx.mock
def test_benchmarks_list_types(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"benchmarkTypes": [{"key": "WEIGHTLIFTING", "displayName": "Weightlifting"}]}})
    )
    result = runner.invoke(app, ["benchmarks"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["benchmarkTypes"][0]["key"] == "WEIGHTLIFTING"


@respx.mock
def test_benchmarks_search(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"benchmarks": [{"workoutUid": "wu-1", "title": "Fran"}]}})
    )
    result = runner.invoke(app, ["benchmarks", "--type", "WEIGHTLIFTING", "--search", "Fran"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["benchmarks"][0]["title"] == "Fran"


@respx.mock
def test_benchmarks_history(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"benchmarkWorkoutHistory": [{"workout": {"title": "Fran"}}]}})
    )
    result = runner.invoke(app, ["benchmarks", "--part-uid", "part-1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["benchmarkWorkoutHistory"][0]["workout"]["title"] == "Fran"


@respx.mock
def test_benchmarks_weightlifting(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"weightliftingWorkoutHistory": [{"workout": {"title": "Clean"}}]}})
    )
    result = runner.invoke(app, ["benchmarks", "--workout-uid", "wu-1"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["weightliftingWorkoutHistory"][0]["workout"]["title"] == "Clean"
