from typer.testing import CliRunner

from ctmkit.cli import app

runner = CliRunner()


def _workzone(tmp_path):
    d = tmp_path / "workzone" / "teams"
    d.mkdir(parents=True)
    (d / "t.yaml").write_text(
        "org: retail\nteam: billing-0225\napps: ['0225']\n"
        "members:\n  - { github: alice, role: release_manager }\n"
    )
    return tmp_path / "workzone"


def test_approval_check_allows_release_manager(tmp_path):
    result = runner.invoke(app, ["approval", "check", "--app", "0225", "--approver", "alice",
                                 "--author", "bob", "--workzone", str(_workzone(tmp_path))])
    assert result.exit_code == 0


def test_approval_check_denies_author(tmp_path):
    result = runner.invoke(app, ["approval", "check", "--app", "0225", "--approver", "alice",
                                 "--author", "alice", "--workzone", str(_workzone(tmp_path))])
    assert result.exit_code == 1
