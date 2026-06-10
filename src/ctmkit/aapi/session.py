"""Automation API session: authentication and a configured HTTP client."""
from __future__ import annotations

from dataclasses import dataclass

import httpx


class AAPIError(RuntimeError):
    """Raised when an Automation API request fails at the transport level."""


@dataclass(frozen=True)
class Session:
    """An authenticated Automation API endpoint.

    Attributes:
        endpoint: Base AAPI URL, e.g. ``https://host:8443/automation-api``.
        api_key: API token sent in the ``x-api-key`` header.
        verify_tls: Whether to verify the server TLS certificate.
    """

    endpoint: str
    api_key: str
    verify_tls: bool = True

    def client(self, *, transport: httpx.BaseTransport | None = None) -> httpx.Client:
        """Create an httpx client preconfigured with auth + base URL.

        Args:
            transport: Optional transport, used to inject mocks in tests.

        Returns:
            A context-managed ``httpx.Client``; callers should use ``with``.
        """
        return httpx.Client(
            base_url=self.endpoint.rstrip("/"),
            headers={"x-api-key": self.api_key},
            verify=self.verify_tls,
            timeout=60.0,
            transport=transport,
        )
