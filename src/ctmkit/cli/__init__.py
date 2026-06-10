"""ctmkit command-line interface (surface/verb structure).

Each surface lives in its own module and is mounted here as a Typer sub-app, so
the CLI reads ``ctmkit <surface> <verb> --options`` (e.g. ``ctmkit deploy run``).
"""
from __future__ import annotations

import typer

from ctmkit.cli import build, deploy, docs, manifests, promote, session

app = typer.Typer(no_args_is_help=True, help="Control-M GitOps toolkit.")
app.add_typer(manifests.app, name="manifests")
app.add_typer(session.app, name="session")
app.add_typer(build.app, name="build")
app.add_typer(deploy.app, name="deploy")
app.add_typer(promote.app, name="promote")
app.add_typer(docs.app, name="docs")
