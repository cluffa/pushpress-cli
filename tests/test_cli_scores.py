from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


@respx.mock
def test_scores_leaderboard(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"workoutGetScores": {"scores": [{"id": 1, "primaryScore": "100"}]}}})
    )
    result = runner.invoke(app, ["scores", "--part-uid", "part-1", "--date", "2026-07-17"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["workoutGetScores"]["scores"][0]["id"] == 1


@respx.mock
def test_scores_keyword_history(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    (tmp_path / "session.json").write_text(json.dumps({
        "clientUuid": "client_1", "userUuid": "usr_1", "accessToken": "tok"
    }))
    respx.post(f"{BASE}/v2/graph/graphql").mock(
        return_value=httpx.Response(200, json={"data": {"scoreHistory": [{"title": "Fran"}]}})
    )
    result = runner.invoke(app, ["scores", "--keyword", "fran"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["scoreHistory"][0]["title"] == "Fran"
