import json
from pathlib import Path

from ctmkit.aapi.models import DeployResult
from ctmkit.deploy.ordered import DeployPlan, ordered_deploy


def _slice(tmp_path):
    base = tmp_path / "control-m/0225/development"
    (base / "connection_profiles").mkdir(parents=True)
    (base / "folders").mkdir(parents=True)
    (base / "connection_profiles/0225_CP.json").write_text(
        json.dumps({"0225_CP": {"Type": "ConnectionProfile:SAP"}}))
    (base / "folders/D0225_F.json").write_text(
        json.dumps({"DEV#D0225_F": {"Type": "Folder"}}))
    return base


def test_plan_orders_connection_profiles_before_folders(tmp_path):
    base = _slice(tmp_path)
    plan = ordered_deploy(base, order=["connection_profiles", "folders"], dry_run=True)
    assert isinstance(plan, DeployPlan)
    assert [step.kind for step in plan.steps] == ["connection_profiles", "folders"]


def test_run_deploys_each_file_via_callback(tmp_path):
    base = _slice(tmp_path)
    calls = []

    def fake_deploy(path: Path) -> DeployResult:
        calls.append(path.name)
        return DeployResult(ok=True, deployed=[path.stem])

    plan = ordered_deploy(base, order=["connection_profiles", "folders"], deploy_fn=fake_deploy)
    assert calls == ["0225_CP.json", "D0225_F.json"]
    assert plan.ok


def test_fail_fast_stops_at_first_error(tmp_path):
    base = _slice(tmp_path)
    calls = []

    def fake_deploy(path: Path) -> DeployResult:
        calls.append(path.name)
        return DeployResult(ok=False, errors=["nope"])

    plan = ordered_deploy(base, order=["connection_profiles", "folders"], deploy_fn=fake_deploy)
    assert calls == ["0225_CP.json"]  # stopped before folders
    assert not plan.ok
