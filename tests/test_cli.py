import json
from pathlib import Path

from typer.testing import CliRunner

from ctmkit.cli import app

runner = CliRunner()
FIX = Path(__file__).parent / "fixtures"


def test_cli_has_validate_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "validate" in result.output


def test_validate_command_passes_on_good_tree(tmp_path):
    p = tmp_path / "control-m/0225/development/calendars/0225_HOLYDAY.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"0225_HOLYDAY": {"Type": "Calendar"}}))
    result = runner.invoke(app, [
        "validate", str(tmp_path),
        "--site-standard", str(FIX / "site-standard.yaml"),
        "--schemas", str(FIX / "schemas"),
    ])
    assert result.exit_code == 0
    assert "OK" in result.output
