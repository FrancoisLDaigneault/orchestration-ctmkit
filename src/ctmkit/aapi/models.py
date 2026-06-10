"""Typed results returned by Automation API service calls."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ObjectStatus:
    """Per-object deployment/build status.

    Attributes:
        name: Object name as reported by Control-M.
        ok: Whether this object succeeded.
        message: Server message (error text when ``ok`` is False).
    """

    name: str
    ok: bool
    message: str = ""


@dataclass
class BuildResult:
    """Outcome of a build (server-side validate) call.

    Attributes:
        ok: True when no errors were reported.
        statuses: Per-object statuses.
        errors: Flat list of error messages.
    """

    ok: bool
    statuses: list[ObjectStatus] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class DeployResult:
    """Outcome of a deploy call.

    Attributes:
        ok: True when the deploy succeeded.
        deployed: Names of successfully deployed objects.
        statuses: Per-object statuses.
        errors: Flat list of error messages.
    """

    ok: bool
    deployed: list[str] = field(default_factory=list)
    statuses: list[ObjectStatus] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
