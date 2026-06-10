"""Automation API deploy service."""
from __future__ import annotations

from pathlib import Path

import httpx

from ctmkit.aapi._summary import summarize
from ctmkit.aapi.models import DeployResult
from ctmkit.aapi.session import AAPIError, Session


def deploy(session: Session, definitions_path: Path, *,
           transport: httpx.BaseTransport | None = None) -> DeployResult:
    """Deploy a single definitions file to Control-M.

    Args:
        session: Authenticated AAPI session.
        definitions_path: Path to a JSON definitions file.
        transport: Optional transport override (tests).

    Returns:
        A :class:`~ctmkit.aapi.models.DeployResult`.

    Raises:
        AAPIError: When the HTTP request fails or returns a non-JSON error.
    """
    path = Path(definitions_path)
    try:
        with session.client(transport=transport) as client, path.open("rb") as fh:
            resp = client.post(
                "/deploy",
                files={"definitionsFile": (path.name, fh, "application/json")})
    except httpx.HTTPError as exc:  # pragma: no cover
        raise AAPIError(f"deploy request failed: {exc}") from exc
    if resp.status_code >= 400 and "json" not in resp.headers.get("content-type", ""):
        raise AAPIError(f"deploy HTTP {resp.status_code}: {resp.text[:200]}")
    statuses, errors = summarize(resp.json())
    deployed = [s.name for s in statuses if s.ok]
    return DeployResult(ok=not errors, deployed=deployed, statuses=statuses, errors=errors)
