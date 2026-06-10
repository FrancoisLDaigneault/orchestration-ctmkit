from ctmkit.approval.policy import can_approve
from ctmkit.approval.registry import Member, Team

TEAMS = [
    Team("billing-0225", "retail", ("0225",),
         (Member("alice", "release_manager"), Member("bob", "developer"))),
]


def test_release_manager_not_author_allowed():
    assert can_approve(TEAMS, app="0225", approver="alice", author="bob").allowed


def test_author_cannot_self_approve():
    d = can_approve(TEAMS, app="0225", approver="alice", author="alice")
    assert not d.allowed and "author" in d.reason.lower()


def test_developer_cannot_approve():
    d = can_approve(TEAMS, app="0225", approver="bob", author="alice")
    assert not d.allowed and "release_manager" in d.reason


def test_unknown_app_denied():
    d = can_approve(TEAMS, app="9999", approver="alice", author="bob")
    assert not d.allowed and "no team" in d.reason.lower()
