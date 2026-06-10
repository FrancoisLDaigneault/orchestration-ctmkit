"""Normalise Automation API status payloads into typed statuses."""
from __future__ import annotations

from ctmkit.aapi.models import ObjectStatus


def summarize(payload: object) -> tuple[list[ObjectStatus], list[str]]:
    """Extract per-object statuses and a flat error list from an AAPI payload.

    Handles both a single object and a list of result blocks, each of which may
    carry ``deploymentStatuses`` and/or top-level ``errors``.

    Args:
        payload: Decoded JSON from a build/deploy response.

    Returns:
        A tuple ``(statuses, errors)``.
    """
    statuses: list[ObjectStatus] = []
    errors: list[str] = []
    blocks = payload if isinstance(payload, list) else [payload]
    for block in blocks:
        if not isinstance(block, dict):
            continue
        for raw in block.get("deploymentStatuses", []) or []:
            ok = bool(raw.get("isSuccessful", False))
            status = ObjectStatus(name=raw.get("name", "?"), ok=ok,
                                  message=raw.get("message", ""))
            statuses.append(status)
            if not ok:
                errors.append(f"{status.name}: {status.message}")
        for err in block.get("errors", []) or []:
            errors.append(str(err.get("message", err) if isinstance(err, dict) else err))
    return statuses, errors
