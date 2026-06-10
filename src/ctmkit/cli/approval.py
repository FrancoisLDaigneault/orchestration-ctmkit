"""`ctmkit approval` surface: enforce the release-manager approval policy."""
from __future__ import annotations

from pathlib import Path

import typer

from ctmkit.approval.policy import can_approve
from ctmkit.approval.registry import load_teams
from ctmkit.cli._console import failure, success

app = typer.Typer(no_args_is_help=True, help="Approval policy checks.")


@app.command()
def check(
    app_id: str = typer.Option(..., "--app"),
    approver: str = typer.Option(..., "--approver", help="Login approving the deploy."),
    author: str = typer.Option(..., "--author", help="PR author login."),
    workzone: Path = typer.Option(Path("workzone"), "--workzone", help="Team registry root."),
) -> None:
    """Exit 0 only if ``--approver`` is a release_manager for ``--app`` and not ``--author``."""
    decision = can_approve(load_teams(workzone), app=app_id, approver=approver, author=author)
    if decision.allowed:
        success(decision.reason)
        raise typer.Exit(0)
    failure(decision.reason)
    raise typer.Exit(1)
