"""`ctmkit session` surface: verify Automation API connectivity."""
from __future__ import annotations

from pathlib import Path

import httpx
import typer

from ctmkit.cli._console import failure, success
from ctmkit.cli._context import resolve_session

app = typer.Typer(no_args_is_help=True, help="Automation API session.")


@app.command()
def login(
    env: str = typer.Option(None, "--env", help="development/staging/production/lab"),
    endpoint: str = typer.Option(None, "--endpoint", help="Override the resolved endpoint."),
    api_key: str = typer.Option(..., "--api-key", envvar="CTM_API_KEY"),
    path: Path = typer.Option(Path("."), "--path", help="Repo root (for --env resolution)."),
) -> None:
    """Verify the endpoint for ``--env`` answers with ``--api-key``."""
    session = resolve_session(path, env, endpoint, api_key)
    try:
        with session.client() as client:
            resp = client.get("/build")  # any response proves auth + reachability
        success(f"reachable: {session.endpoint} (HTTP {resp.status_code})")
    except httpx.HTTPError as exc:
        failure(f"unreachable: {exc}")
        raise typer.Exit(1)
