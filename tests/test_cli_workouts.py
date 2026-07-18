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
