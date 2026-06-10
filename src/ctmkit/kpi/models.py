"""KPI data model for a single deploy."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass
class DeployKpi:
    """Metrics for one deploy run.

    Attributes:
        app: Application id (e.g. ``0225``).
        env: Environment name.
        objects: Number of objects in the plan.
        succeeded: Number deployed successfully.
        failed: Number that failed.
        duration_s: Wall-clock duration in seconds.
        ok: Whether the deploy as a whole succeeded.
        blackout_deferred: Whether the deploy was blocked by a blackout window.
        timestamp: ISO-8601 UTC timestamp.
        approver: GitHub login that approved the deploy (if any).
    """

    app: str
    env: str
    objects: int
    succeeded: int
    failed: int
    duration_s: float
    ok: bool
    timestamp: str
    blackout_deferred: bool = False
    approver: str | None = None

    def to_json(self) -> str:
        """Return the KPI as a compact JSON object string."""
        return json.dumps(asdict(self), separators=(",", ":"))
