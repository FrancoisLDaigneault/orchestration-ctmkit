"""The approval decision: a release manager who is not the PR author."""
from __future__ import annotations

from dataclasses import dataclass

from ctmkit.approval.registry import Team, team_for_app


@dataclass
class Decision:
    """The outcome of an approval check.

    Attributes:
        allowed: Whether the approval is permitted.
        reason: Human-readable explanation (for the PR comment / logs).
    """

    allowed: bool
    reason: str


def can_approve(teams: list[Team], *, app: str, approver: str, author: str) -> Decision:
    """Decide whether ``approver`` may approve a deploy of ``app`` authored by ``author``.

    The approver must be a ``release_manager`` on the team that owns ``app`` and must not be
    the PR author (separation of duties).

    Args:
        teams: The loaded team registry.
        app: Application id being deployed.
        approver: GitHub login of the person approving.
        author: GitHub login of the PR author.

    Returns:
        A :class:`Decision`.
    """
    if approver == author:
        return Decision(False,
                        f"@{approver} is the PR author — a different release manager must approve")
    team = team_for_app(teams, app)
    if team is None:
        return Decision(False, f"no team owns app {app}")
    role = team.role_of(approver)
    if role != "release_manager":
        return Decision(False,
                        f"@{approver} is not a release_manager for {team.name} "
                        f"(role: {role or 'none'})")
    return Decision(True, f"@{approver} is a release_manager for {team.name} and not the author")
