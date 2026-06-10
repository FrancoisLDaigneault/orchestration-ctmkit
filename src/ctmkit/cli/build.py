"""`ctmkit build` surface: server-side validate via the AAPI build service."""
from __future__ import annotations

from pathlib import Path

import typer

from ctmkit.aapi.build import build
from ctmkit.cli._console import errors_table, failure, success
from ctmkit.cli._context import resolve_session

app = typer.Typer(no_args_is_help=True, help="Server-side validate (AAPI build).")


@app.command()
def run(
    file: Path = typer.Option(..., "--file", help="Definitions JSON file."),
    env: str = typer.Option(None, "--env", help="development/staging/production/lab"),
    endpoint: str = typer.Option(None, "--endpoint", help="Override the resolved endpoint."),
    api_key: str = typer.Option(..., "--api-key", envvar="CTM_API_KEY"),
    path: Path = typer.Option(Path("."), "--path", help="Repo root (for --env resolution)."),
) -> None:
    """Validate ``--file`` against Control-M without deploying."""
    session = resolve_session(path, env, endpoint, api_key)
    result = build(session, file)
    if result.ok:
        success(f"{file.name} is valid")
        raise typer.Exit(0)
    errors_table("build errors", result.errors)
    failure(f"{len(result.errors)} error(s)")
    raise typer.Exit(1)
