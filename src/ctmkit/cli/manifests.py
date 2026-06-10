"""`ctmkit manifests` surface: validate the manifests repo."""
from __future__ import annotations

from pathlib import Path

import typer

from ctmkit.cli._console import errors_table, failure, success
from ctmkit.validate import validate_tree

app = typer.Typer(no_args_is_help=True, help="Operate on the manifests repo.")


@app.command()
def validate(
    path: Path = typer.Option(Path("."), "--path", help="Repo root or subtree."),
    site_standard: Path = typer.Option(Path("config/site-standard.yaml"), "--site-standard"),
    schemas: Path = typer.Option(Path("schemas"), "--schemas"),
) -> None:
    """Validate manifests under ``--path`` (schema + nomenclature).

    Exits non-zero when any problem is found.
    """
    report = validate_tree(path, site_standard=site_standard, schemas_dir=schemas)
    if report.ok:
        success("all manifests valid")
        raise typer.Exit(0)
    errors_table(f"{len(report.errors)} problem(s)", report.errors)
    failure(f"{len(report.errors)} problem(s)")
    raise typer.Exit(1)
