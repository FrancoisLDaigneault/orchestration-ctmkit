"""Shared CLI helpers: resolve an AAPI session from ``--env`` or ``--endpoint``."""
from __future__ import annotations

from pathlib import Path

import typer

from ctmkit.aapi.session import Session
from ctmkit.config import load_environments


def resolve_session(repo: Path, env: str | None, endpoint: str | None, api_key: str) -> Session:
    """Build a :class:`Session` from an explicit endpoint or by resolving ``--env``.

    ``--endpoint`` wins when given; otherwise the endpoint is looked up for ``env``
    in ``<repo>/config/environments.yaml``.

    Args:
        repo: Repo root holding ``config/environments.yaml``.
        env: Environment name (development/staging/production/lab).
        endpoint: Explicit AAPI base URL (overrides env resolution).
        api_key: AAPI API key.

    Returns:
        A configured :class:`Session`.

    Raises:
        typer.BadParameter: When neither a valid env nor an endpoint is provided.
    """
    if endpoint:
        return Session(endpoint=endpoint, api_key=api_key)
    if not env:
        raise typer.BadParameter("provide --env or --endpoint")
    envs = load_environments(Path(repo) / "config" / "environments.yaml")
    if env not in envs:
        raise typer.BadParameter(f"unknown env {env!r}; known: {', '.join(envs)}")
    return Session(endpoint=envs[env].endpoint, api_key=api_key)
