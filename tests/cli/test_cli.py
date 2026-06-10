import json
from pathlib import Path

from typer.testing import CliRunner

from ctmkit.cli import app

runner = CliRunner()
FIX = Path(__file__).parents[1] / "fixtures"


def test_root_help_lists_surfaces():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for surface in ("manifests", "session", "build", "deploy", "promote", "approval",
                    "events", "mcp"):
        assert surface in result.output


def test_manifests_validate_ok(tmp_path):
    p = tmp_path / "control-m/0225/development/calendars/0225_HOLYDAY.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"0225_HOLYDAY": {"Type": "Calendar"}}))
    result = runner.invoke(app, [
        "manifests", "validate", "--path", str(tmp_path),
        "--site-standard", str(FIX / "site-standard.yaml"),
        "--schemas", str(FIX / "schemas"),
    ])
    assert result.exit_code == 0
    assert "valid" in result.output.lower()
