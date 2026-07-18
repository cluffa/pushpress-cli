import json

from typer.testing import CliRunner

from pp.cli import app
from pp.describe import catalog

runner = CliRunner()


def test_catalog_covers_commands():
    names = {c["command"] for c in catalog()}
    assert {"gym", "features", "settings", "feed", "graphql", "raw", "whoami", "appointments"} <= names


def test_describe_all_is_json_list():
    result = runner.invoke(app, ["describe"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list) and any(c["command"] == "gym" for c in data)


def test_describe_unknown_errors():
    result = runner.invoke(app, ["describe", "nope"])
    assert result.exit_code == 4
    assert json.loads(result.stderr)["code"] == "not_found"
