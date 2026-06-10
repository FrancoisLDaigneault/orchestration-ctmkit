"""Automation API build (server-side validate) service."""
from __future__ import annotations

from pathlib import Path

import httpx

from ctmkit.aapi._summary import summarize
from ctmkit.aapi.models import BuildResult
from ctmkit.aapi.session import AAPIError, Session


def build(session: Session, definitions_path: Path, *,
          transport: httpx.BaseTransport | None = None) -> BuildResult:
    """Validate a definitions file via the build service (no deploy).

    Args:
        session: Authenticated AAPI session.
        definitions_path: Path to a JSON definitions file.
        transport: Optional transport override (tests).

    Returns:
        A :class:`~ctmkit.aapi.models.BuildResult`.

    Raises:
        AAPIError: When the HTTP request fails or returns a non-JSON error.
    """
    path = Path(definitions_path)
    try:
        with session.client(transport=transport) as client, path.open("rb") as fh:
            resp = client.post(
                "/build",
                files={"definitionsFile": (path.name, fh, "application/json")})
    except httpx.HTTPError as exc:  # pragma: no cover - network failure path
        raise AAPIError(f"build request failed: {exc}") from exc
    if resp.status_code >= 400 and "json" not in resp.headers.get("content-type", ""):
        raise AAPIError(f"build HTTP {resp.status_code}: {resp.text[:200]}")
    statuses, errors = summarize(resp.json())
    return BuildResult(ok=not errors, statuses=statuses, errors=errors)
