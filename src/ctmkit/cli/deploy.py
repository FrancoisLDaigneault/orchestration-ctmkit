"""`ctmkit deploy` surface: ordered deploy of a manifests subtree, with guardrails."""
from __future__ import annotations

import time as _time
from datetime import UTC, datetime
from pathlib import Path

import typer
from rich.table import Table

from ctmkit.aapi.deploy import deploy
from ctmkit.cli._console import console, failure, success
from ctmkit.cli._context import resolve_session
from ctmkit.config import load_deploy_order
from ctmkit.deploy.ordered import DeployPlan, ordered_deploy
from ctmkit.kpi.emit import append_jsonl, summary_line
from ctmkit.kpi.models import DeployKpi
from ctmkit.policy.blackout import in_blackout
from ctmkit.policy.health import server_healthy

app = typer.Typer(no_args_is_help=True, help="Deploy manifests to Control-M.")

_DEFAULT_ORDER = ["secrets", "connection_profiles", "calendars", "quantitative_ressources",
                  "plugins", "agents", "event_driven", "folders", "services"]


def _subtree(repo: Path, app_id: str, env: str) -> Path:
    return Path(repo) / "control-m" / app_id / env


def _order(repo: Path) -> list[str]:
    cfg = Path(repo) / "config" / "deploy-order.yaml"
    return load_deploy_order(cfg) if cfg.exists() else list(_DEFAULT_ORDER)


def _render(plan: DeployPlan) -> None:
    table = Table(title="deploy plan")
    table.add_column("#", justify="right")
    table.add_column("phase")
    table.add_column("file")
    table.add_column("status")
    for i, step in enumerate(plan.steps, 1):
        status = "planned" if step.result is None else ("ok" if step.result.ok else "FAILED")
        table.add_row(str(i), step.kind, step.path.name, status)
    console.print(table)


@app.command()
def plan(
    app_id: str = typer.Option(..., "--app"),
    env: str = typer.Option(..., "--env"),
    path: Path = typer.Option(Path("."), "--path", help="Repo root."),
) -> None:
    """Show what would deploy (order + files), without contacting Control-M."""
    _render(ordered_deploy(_subtree(path, app_id, env), order=_order(path), dry_run=True))


@app.command()
def run(
    app_id: str = typer.Option(..., "--app"),
    env: str = typer.Option(..., "--env"),
    path: Path = typer.Option(Path("."), "--path", help="Repo root."),
    endpoint: str = typer.Option(None, "--endpoint", help="Override the resolved endpoint."),
    api_key: str = typer.Option(..., "--api-key", envvar="CTM_API_KEY"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Plan only; do not deploy."),
    force: bool = typer.Option(False, "--force", help="Override the replan blackout window."),
    kpi_out: Path = typer.Option(None, "--kpi-out", help="Append a KPI record to this JSONL file."),
    approver: str = typer.Option(None, "--approver", help="Login that approved (for KPIs)."),
) -> None:
    """Deploy ``--app``/``--env`` in order, one file at a time, fail-fast.

    Guardrails: refuses to deploy within the noon/midnight replan blackout (unless
    ``--force``) and gates on Control-M server health. Emits a KPI record.
    """
    subtree = _subtree(path, app_id, env)
    if dry_run:
        _render(ordered_deploy(subtree, order=_order(path), dry_run=True))
        success("dry-run: nothing deployed")
        raise typer.Exit(0)

    window = in_blackout(datetime.now())
    if window and not force:
        failure(f"blackout: within ±{window.margin_minutes}min of "
                f"{window.at.strftime('%H:%M')} replan — use --force to override")
        raise typer.Exit(2)

    session = resolve_session(path, env, endpoint, api_key)
    if not server_healthy(session):
        failure("server health check failed — aborting deploy")
        raise typer.Exit(2)

    started = _time.monotonic()
    result = ordered_deploy(subtree, order=_order(path),
                            deploy_fn=lambda p: deploy(session, p))
    _render(result)

    succeeded = sum(1 for s in result.steps if s.result and s.result.ok)
    kpi = DeployKpi(
        app=app_id, env=env, objects=len(result.steps), succeeded=succeeded,
        failed=len(result.steps) - succeeded, duration_s=_time.monotonic() - started,
        ok=result.ok, timestamp=datetime.now(UTC).isoformat(), approver=approver,
    )
    console.print(summary_line(kpi))
    if kpi_out:
        append_jsonl(kpi, kpi_out)

    if result.ok:
        success("deploy complete")
        raise typer.Exit(0)
    failure("deploy failed (stopped at first error)")
    raise typer.Exit(1)
