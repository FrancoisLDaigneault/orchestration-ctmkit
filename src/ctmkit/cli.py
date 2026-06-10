"""ctmkit command-line interface."""
from pathlib import Path

import typer

from ctmkit.validate import validate_tree

app = typer.Typer(no_args_is_help=True, help="Control-M GitOps toolkit.")


@app.callback()
def _main() -> None:
    """Control-M GitOps toolkit (force subcommand routing even with one command)."""


@app.command()
def validate(
    path: Path = typer.Argument(..., help="Repo root or subtree to validate."),
    site_standard: Path = typer.Option(Path("config/site-standard.yaml"), "--site-standard"),
    schemas: Path = typer.Option(Path("schemas"), "--schemas"),
) -> None:
    """Validate manifests under PATH (schema + nomenclature)."""
    report = validate_tree(path, site_standard=site_standard, schemas_dir=schemas)
    if report.ok:
        typer.echo("OK — all manifests valid")
        raise typer.Exit(0)
    for err in report.errors:
        typer.echo(f"ERROR {err}")
    typer.echo(f"\n{len(report.errors)} problem(s)")
    raise typer.Exit(1)
