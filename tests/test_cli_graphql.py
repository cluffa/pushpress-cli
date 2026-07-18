import json

from typer.testing import CliRunner

from pp.cli import app

runner = CliRunner()


def _session(tmp_path, monkeypatch):
    monkeypatch.setenv("PP_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("PP_TOKEN", "tok")


def test_graphql_rejects_malformed_vars(tmp_path, monkeypatch):
    _session(tmp_path, monkeypatch)
    result = runner.invoke(app, ["graphql", "-q", "{__typename}", "--vars", "not-json"])
    assert result.exit_code == 2
    assert json.loads(result.stderr)["code"] == "usage"
