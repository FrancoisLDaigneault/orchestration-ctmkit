import json

from ctmkit.mcp import tools


def _repo(tmp_path):
    base = tmp_path
    (base / "config").mkdir()
    (base / "config/site-standard.yaml").write_text(
        "distributed_letter: 'D'\napp_ids: ['0225']\nenvironments:\n"
        "  development: { token: DEV, server: CTMDEV }\n")
    (base / "schemas").mkdir()
    (base / "schemas/calendar.schema.json").write_text(json.dumps({
        "type": "object", "additionalProperties": {"type": "object", "required": ["Type"]}}))
    cal = base / "control-m/0225/development/calendars"
    cal.mkdir(parents=True)
    (cal / "0225_HOLYDAY.json").write_text(json.dumps({"0225_HOLYDAY": {"Type": "Calendar"}}))
    return base


def test_validate_manifests_ok(tmp_path):
    out = tools.validate_manifests(str(_repo(tmp_path)))
    assert out["ok"] is True and out["errors"] == []


def test_deploy_plan_lists_steps(tmp_path):
    plan = tools.deploy_plan("0225", "development", str(_repo(tmp_path)))
    assert any(s["file"] == "0225_HOLYDAY.json" for s in plan)


def test_blackout_status_shape():
    out = tools.blackout_status()
    assert set(out) == {"in_blackout", "window"}


def test_approval_check(tmp_path):
    base = tmp_path
    wz = base / "workzone/teams"
    wz.mkdir(parents=True)
    (wz / "t.yaml").write_text(
        "org: o\nteam: billing-0225\napps: ['0225']\n"
        "members:\n  - { github: alice, role: release_manager }\n")
    assert tools.approval_check("0225", "alice", "bob", str(base))["allowed"] is True
    assert tools.approval_check("0225", "alice", "alice", str(base))["allowed"] is False
