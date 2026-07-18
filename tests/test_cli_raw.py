import json

import httpx
import respx
from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()
BASE = "https://api.pushpress.com"


def _session(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("PP_TOKEN", "tok")


def test_raw_rejects_non_get(tmp_path, monkeypatch):
    _session(tmp_path, monkeypatch)
    result = runner.invoke(app, ["raw", "POST", "/v2/x"])
    assert result.exit_code == 2
    assert json.loads(result.stderr)["code"] == "usage"


@respx.mock
def test_raw_get_ok(tmp_path, monkeypatch):
    _session(tmp_path, monkeypatch)
    respx.get(f"{BASE}/v2/ping").mock(return_value=httpx.Response(200, json={"pong": True}))
    result = runner.invoke(app, ["raw", "GET", "/v2/ping"])
    assert json.loads(result.stdout) == {"pong": True}
