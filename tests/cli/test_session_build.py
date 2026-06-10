from pathlib import Path

from typer.testing import CliRunner

from ctmkit.aapi.models import BuildResult
from ctmkit.cli import app

runner = CliRunner()


def test_build_run_reports_ok(tmp_path, monkeypatch):
    f = tmp_path / "0225_X.json"
    f.write_text("{}")
    monkeypatch.setattr("ctmkit.cli.build.build", lambda *a, **k: BuildResult(ok=True))
    result = runner.invoke(app, ["build", "run", "--file", str(f),
                                 "--endpoint", "https://ctm/automation-api", "--api-key", "K"])
    assert result.exit_code == 0
    assert "valid" in result.output.lower()


def test_build_run_fails_with_errors(tmp_path, monkeypatch):
    f = tmp_path / "0225_X.json"
    f.write_text("{}")
    monkeypatch.setattr("ctmkit.cli.build.build",
                        lambda *a, **k: BuildResult(ok=False, errors=["bad"]))
    result = runner.invoke(app, ["build", "run", "--file", str(f),
                                 "--endpoint", "https://ctm/automation-api", "--api-key", "K"])
    assert result.exit_code == 1
    assert "bad" in result.output
