"""`ctmkit deploy` surface: ordered deploy of a manifests subtree."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.table import Table

from ctmkit.aapi.deploy import deploy
from ctmkit.cli._console import console, failure, success
from ctmkit.cli._context import resolve_session
from ctmkit.config import load_deploy_order
from ctmkit.deploy.ordered import DeployPlan, ordered_deploy

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
) -> None:
    """Deploy ``--app``/``--env`` in order, one file at a time, fail-fast."""
    subtree = _subtree(path, app_id, env)
    if dry_run:
        _render(ordered_deploy(subtree, order=_order(path), dry_run=True))
        success("dry-run: nothing deployed")
        raise typer.Exit(0)
    session = resolve_session(path, env, endpoint, api_key)
    result = ordered_deploy(subtree, order=_order(path),
                            deploy_fn=lambda p: deploy(session, p))
    _render(result)
    if result.ok:
        success("deploy complete")
        raise typer.Exit(0)
    failure("deploy failed (stopped at first error)")
    raise typer.Exit(1)
