"""Emit deploy KPIs to JSON Lines + a human summary (pluggable sink)."""
from __future__ import annotations

from pathlib import Path

from ctmkit.kpi.models import DeployKpi


def append_jsonl(kpi: DeployKpi, path: Path) -> None:
    """Append one KPI record as a JSON line to ``path`` (creating dirs).

    Args:
        kpi: The KPI to record.
        path: Target ``.jsonl`` file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(kpi.to_json() + "\n")


def summary_line(kpi: DeployKpi) -> str:
    """Return a one-line human summary of a KPI.

    Args:
        kpi: The KPI to render.

    Returns:
        A compact human-readable line.
    """
    status = "ok" if kpi.ok else "FAILED"
    return (f"{kpi.app}/{kpi.env}: {kpi.succeeded}/{kpi.objects} deployed "
            f"in {kpi.duration_s:.1f}s [{status}]")
