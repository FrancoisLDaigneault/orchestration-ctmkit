"""Load the workzone team/role registry (teams own apps; members have roles)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

VALID_ROLES = frozenset({"developer", "release_manager", "support"})


@dataclass(frozen=True)
class Member:
    """A team member and their role.

    Attributes:
        github: GitHub login.
        role: One of ``developer`` / ``release_manager`` / ``support``.
    """

    github: str
    role: str


@dataclass(frozen=True)
class Team:
    """A team that owns one or more applications.

    Attributes:
        name: Team name.
        org: Owning organisation/business unit.
        apps: Application ids this team owns.
        members: Team members.
    """

    name: str
    org: str
    apps: tuple[str, ...]
    members: tuple[Member, ...]

    def role_of(self, github: str) -> str | None:
        """Return ``github``'s role on this team, or None if not a member.

        Args:
            github: GitHub login to look up.

        Returns:
            The role string, or None.
        """
        for member in self.members:
            if member.github == github:
                return member.role
        return None


def load_teams(workzone_dir: Path) -> list[Team]:
    """Load every team from ``<workzone_dir>/teams/*.yaml``.

    Args:
        workzone_dir: Path to the workzone registry root.

    Returns:
        The parsed teams (possibly empty).
    """
    teams: list[Team] = []
    for path in sorted((Path(workzone_dir) / "teams").glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        members = tuple(
            Member(github=m["github"], role=m["role"]) for m in data.get("members", [])
        )
        teams.append(Team(
            name=data["team"], org=data["org"],
            apps=tuple(str(a) for a in data.get("apps", [])), members=members,
        ))
    return teams


def team_for_app(teams: list[Team], app: str) -> Team | None:
    """Return the team owning ``app``, or None.

    Args:
        teams: All teams.
        app: Application id.

    Returns:
        The owning :class:`Team`, or None.
    """
    for team in teams:
        if app in team.apps:
            return team
    return None
