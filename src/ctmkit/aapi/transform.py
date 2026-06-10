"""Automation API deploy/transform service (apply a deploy descriptor)."""
from __future__ import annotations

from pathlib import Path

import httpx

from ctmkit.aapi.session import AAPIError, Session


def transform(session: Session, definitions_path: Path, descriptor_path: Path, *,
              transport: httpx.BaseTransport | None = None) -> str:
    """Apply a deploy descriptor to a definitions file and return the result JSON.

    Args:
        session: Authenticated AAPI session.
        definitions_path: Path to the source definitions JSON.
        descriptor_path: Path to the deploy-descriptor JSON.
        transport: Optional transport override (tests).

    Returns:
        The transformed definitions as a JSON string.

    Raises:
        AAPIError: When the HTTP request fails or returns a non-2xx status.
    """
    defs, desc = Path(definitions_path), Path(descriptor_path)
    try:
        with session.client(transport=transport) as client, \
                defs.open("rb") as df, desc.open("rb") as cf:
            resp = client.post("/deploy/transform", files={
                "definitionsFile": (defs.name, df, "application/json"),
                "deployDescriptorFile": (desc.name, cf, "application/json"),
            })
    except httpx.HTTPError as exc:  # pragma: no cover
        raise AAPIError(f"transform request failed: {exc}") from exc
    if resp.status_code >= 400:
        raise AAPIError(f"transform HTTP {resp.status_code}: {resp.text[:200]}")
    return resp.text
