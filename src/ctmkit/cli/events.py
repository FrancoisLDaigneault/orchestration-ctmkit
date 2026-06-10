"""`ctmkit events` surface: validate + render Kafka/SQS event sources."""
from __future__ import annotations

import json
from pathlib import Path

import typer

from ctmkit.cli._console import console, errors_table, failure, success
from ctmkit.events.models import validate_event_source
from ctmkit.events.render import render_handler_config

app = typer.Typer(no_args_is_help=True, help="Event-driven (Kafka/SQS) sources.")


def _load_sources(repo: Path, app_id: str, env: str) -> list[tuple[str, dict]]:
    src_dir = Path(repo) / "control-m" / app_id / env / "event_driven"
    sources: list[tuple[str, dict]] = []
    for path in sorted(src_dir.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        name = next(iter(obj))
        sources.append((name, obj[name]))
    return sources


@app.command()
def validate(
    app_id: str = typer.Option(..., "--app"),
    env: str = typer.Option(..., "--env"),
    path: Path = typer.Option(Path("."), "--path", help="Repo root."),
) -> None:
    """Validate the Kafka/SQS event sources for ``--app``/``--env``."""
    errors: list[str] = []
    for name, body in _load_sources(path, app_id, env):
        errors += validate_event_source(name, body)
    if not errors:
        success("event sources valid")
        raise typer.Exit(0)
    errors_table("event errors", errors)
    failure(f"{len(errors)} problem(s)")
    raise typer.Exit(1)


@app.command()
def render(
    app_id: str = typer.Option(..., "--app"),
    env: str = typer.Option(..., "--env"),
    path: Path = typer.Option(Path("."), "--path", help="Repo root."),
) -> None:
    """Render the Control-M Event Handler queue-config YAML for ``--app``/``--env``."""
    console.print(render_handler_config(_load_sources(path, app_id, env)))
