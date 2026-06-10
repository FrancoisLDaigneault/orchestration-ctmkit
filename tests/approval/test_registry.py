from ctmkit.approval.registry import load_teams, team_for_app


def _workzone(tmp_path):
    d = tmp_path / "workzone" / "teams"
    d.mkdir(parents=True)
    (d / "billing.yaml").write_text(
        "org: retail\nteam: billing-0225\napps: ['0225']\n"
        "members:\n  - { github: alice, role: release_manager }\n"
        "  - { github: bob, role: developer }\n"
    )
    return tmp_path / "workzone"


def test_load_and_lookup(tmp_path):
    teams = load_teams(_workzone(tmp_path))
    assert len(teams) == 1
    team = team_for_app(teams, "0225")
    assert team.name == "billing-0225"
    assert team.role_of("alice") == "release_manager"
    assert team.role_of("bob") == "developer"
    assert team.role_of("zoe") is None


def test_team_for_unknown_app(tmp_path):
    assert team_for_app(load_teams(_workzone(tmp_path)), "9999") is None
