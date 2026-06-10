"""Ordered deployment of a manifests subtree, one file at a time, fail-fast."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from ctmkit.aapi.models import DeployResult

DeployFn = Callable[[Path], DeployResult]


@dataclass
class DeployStep:
    """A single file scheduled for deployment.

    Attributes:
        kind: Object-kind phase (e.g. ``folders``).
        path: File to deploy.
        result: Result after running, or None when planned/dry-run.
    """

    kind: str
    path: Path
    result: DeployResult | None = None


@dataclass
class DeployPlan:
    """An ordered set of deploy steps and the run outcome.

    Attributes:
        steps: Ordered steps.
        ok: True when every executed step succeeded (True for dry-run plans).
    """

    steps: list[DeployStep] = field(default_factory=list)
    ok: bool = True


def _gather(root: Path, order: list[str]) -> list[DeployStep]:
    """Collect deployable files grouped by phase, in order (descriptors excluded)."""
    steps: list[DeployStep] = []
    for kind in order:
        kind_dir = root / kind
        if not kind_dir.is_dir():
            continue
        for path in sorted(kind_dir.glob("*.json")):
            steps.append(DeployStep(kind=kind, path=path))
    return steps


def ordered_deploy(root: Path, *, order: list[str], deploy_fn: DeployFn | None = None,
                   dry_run: bool = False) -> DeployPlan:
    """Plan (and optionally run) an ordered deploy of a manifests subtree.

    Files are deployed phase-by-phase per ``order``, one at a time. Execution
    stops at the first failing file (fail-fast).

    Args:
        root: A ``control-m/<app>/<env>`` directory.
        order: Object-kind phases in deploy order.
        deploy_fn: Callback that deploys one file and returns a result. Required
            unless ``dry_run`` is True.
        dry_run: When True, only build the plan; do not deploy.

    Returns:
        A :class:`DeployPlan`.

    Raises:
        ValueError: If ``deploy_fn`` is missing for a non-dry-run.
    """
    plan = DeployPlan(steps=_gather(Path(root), order))
    if dry_run:
        return plan
    if deploy_fn is None:
        raise ValueError("deploy_fn is required when dry_run is False")
    for step in plan.steps:
        result = deploy_fn(step.path)
        step.result = result
        if not result.ok:
            plan.ok = False
            break
    return plan
