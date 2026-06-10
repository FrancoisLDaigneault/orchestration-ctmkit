import json

from typer.testing import CliRunner

from ctmkit.cli import app

runner = CliRunner()


def _slice(tmp_path):
    d = tmp_path / "control-m/0225/development/folders"
    d.mkdir(parents=True)
    (d / "D0225_F.json").write_text(json.dumps({"DEV#D0225_F": {"Type": "Folder"}}))
    return tmp_path


def test_deploy_plan_lists_steps_without_network(tmp_path):
    _slice(tmp_path)
    result = runner.invoke(app, ["deploy", "plan", "--app", "0225", "--env", "development",
                                 "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "D0225_F.json" in result.output


def test_deploy_run_dry_run_does_not_call_aapi(tmp_path, monkeypatch):
    _slice(tmp_path)
    called = []
    monkeypatch.setattr("ctmkit.cli.deploy.deploy", lambda *a, **k: called.append(1))
    result = runner.invoke(app, ["deploy", "run", "--app", "0225", "--env", "development",
                                 "--path", str(tmp_path), "--endpoint", "https://x",
                                 "--api-key", "K", "--dry-run"])
    assert result.exit_code == 0 and called == []
