"""Plain functions backing the ctmkit MCP tools (tested without an MCP server).

These are read-mostly, GitOps-aware operations safe for an AI agent to call; actually
deploying stays a human-gated CLI/CI action.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ctmkit.approval.policy import can_approve
from ctmkit.approval.registry import load_teams
from ctmkit.config import load_deploy_order
from ctmkit.deploy.ordered import ordered_deploy
from ctmkit.policy.blackout import in_blackout
from ctmkit.validate import validate_tree

_DEFAULT_ORDER = ["secrets", "connection_profiles", "calendars", "quantitative_ressources",
                  "plugins", "agents", "event_driven", "folders", "services"]


def _order(repo: Path) -> list[str]:
    cfg = Path(repo) / "config" / "deploy-order.yaml"
    return load_deploy_order(cfg) if cfg.exists() else list(_DEFAULT_ORDER)


def validate_manifests(path: str = ".") -> dict:
    """Validate the manifests repo (JSON schema + nomenclature / site standard).

    Args:
        path: Repo root.

    Returns:
        ``{"ok": bool, "errors": list[str]}``.
    """
    repo = Path(path)
    report = validate_tree(repo, site_standard=repo / "config/site-standard.yaml",
                           schemas_dir=repo / "schemas")
    return {"ok": report.ok, "errors": report.errors}


def deploy_plan(app: str, env: str, path: str = ".") -> list[dict]:
    """Preview the ordered deploy plan for an app/environment (no deploy).

    Args:
        app: Application id (e.g. ``0225``).
        env: Environment (``development`` / ``staging`` / ``production`` / ``lab``).
        path: Repo root.

    Returns:
        Ordered ``[{"phase": ..., "file": ...}]`` steps.
    """
    plan = ordered_deploy(Path(path) / "control-m" / app / env, order=_order(path), dry_run=True)
    return [{"phase": step.kind, "file": step.path.name} for step in plan.steps]


def blackout_status() -> dict:
    """Report whether deploys are currently in a replan blackout window.

    Returns:
        ``{"in_blackout": bool, "window": "HH:MM" | None}``.
    """
    window = in_blackout(datetime.now())
    return {"in_blackout": window is not None,
            "window": window.at.strftime("%H:%M") if window else None}


def approval_check(app: str, approver: str, author: str,
                   path: str = ".", workzone: str = "workzone") -> dict:
    """Check whether an approver may approve a deploy (release_manager, not the author).

    Args:
        app: Application id.
        approver: GitHub login approving.
        author: PR author login.
        path: Repo root.
        workzone: Team-registry directory (relative to ``path``).

    Returns:
        ``{"allowed": bool, "reason": str}``.
    """
    decision = can_approve(load_teams(Path(path) / workzone),
                           app=app, approver=approver, author=author)
    return {"allowed": decision.allowed, "reason": decision.reason}
