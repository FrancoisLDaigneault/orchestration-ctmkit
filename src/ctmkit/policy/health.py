"""Pre-deploy Control-M server-health gate."""
from __future__ import annotations

import httpx

from ctmkit.aapi.session import Session


def server_healthy(session: Session, *, path: str = "/config/servers",
                   transport: httpx.BaseTransport | None = None) -> bool:
    """Return True if the Control-M endpoint answers a status check.

    A reachable Automation API returning a non-5xx response is treated as healthy.

    Args:
        session: Authenticated AAPI session.
        path: Status endpoint to probe.
        transport: Optional transport override (tests).

    Returns:
        Whether the server appears up and reachable.
    """
    try:
        with session.client(transport=transport) as client:
            resp = client.get(path)
        return resp.status_code < 500
    except httpx.HTTPError:
        return False
