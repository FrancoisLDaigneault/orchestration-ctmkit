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


def _argv(tmp_path, *extra):
    return ["deploy", "run", "--app", "0225", "--env", "development", "--path", str(tmp_path),
            "--endpoint", "https://x", "--api-key", "K", *extra]


def test_deploy_run_blocked_by_blackout(tmp_path, monkeypatch):
    from datetime import time

    from ctmkit.policy.blackout import BlackoutWindow
    _slice(tmp_path)
    monkeypatch.setattr("ctmkit.cli.deploy.in_blackout", lambda now: BlackoutWindow(time(12, 0)))
    result = runner.invoke(app, _argv(tmp_path))
    assert result.exit_code == 2 and "blackout" in result.output.lower()


def test_deploy_run_blocked_when_server_unhealthy(tmp_path, monkeypatch):
    _slice(tmp_path)
    monkeypatch.setattr("ctmkit.cli.deploy.in_blackout", lambda now: None)
    monkeypatch.setattr("ctmkit.cli.deploy.server_healthy", lambda s: False)
    result = runner.invoke(app, _argv(tmp_path))
    assert result.exit_code == 2 and "health" in result.output.lower()


def test_deploy_run_success_emits_kpi(tmp_path, monkeypatch):
    from ctmkit.aapi.models import DeployResult
    _slice(tmp_path)
    monkeypatch.setattr("ctmkit.cli.deploy.in_blackout", lambda now: None)
    monkeypatch.setattr("ctmkit.cli.deploy.server_healthy", lambda s: True)
    monkeypatch.setattr("ctmkit.cli.deploy.deploy",
                        lambda session, p: DeployResult(ok=True, deployed=[p.stem]))
    kpi = tmp_path / "kpi.jsonl"
    result = runner.invoke(app, _argv(tmp_path, "--kpi-out", str(kpi)))
    assert result.exit_code == 0 and "deploy complete" in result.output
    assert kpi.exists() and "0225" in kpi.read_text()
