"""Deploy blackout windows around the Control-M noon/midnight replan.

Control-M reorganises the active jobs at fixed times (the "New Day"/replan, here noon and
midnight). Deploying inside that window risks racing the reorg, so we refuse to deploy within
a small margin of those times.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta


@dataclass(frozen=True)
class BlackoutWindow:
    """A daily blackout centred on a clock time.

    Attributes:
        at: The clock time to avoid (e.g. ``time(12, 0)``, ``time(0, 0)``).
        margin_minutes: Minutes before and after ``at`` that are blacked out.
    """

    at: time
    margin_minutes: int = 5

    def contains(self, now: datetime) -> bool:
        """Return True if ``now`` is within ``margin_minutes`` of ``at`` (any day).

        Handles midnight wrap-around (e.g. 23:57 is inside a 00:00 ± 5 window).

        Args:
            now: The instant to test (naive local time).

        Returns:
            Whether ``now`` falls inside the window.
        """
        center = now.replace(hour=self.at.hour, minute=self.at.minute,
                             second=0, microsecond=0)
        deltas = (
            abs((now - center).total_seconds()),
            abs((now - (center - timedelta(days=1))).total_seconds()),
            abs((now - (center + timedelta(days=1))).total_seconds()),
        )
        return min(deltas) <= self.margin_minutes * 60


DEFAULT_WINDOWS: tuple[BlackoutWindow, ...] = (
    BlackoutWindow(time(12, 0)),
    BlackoutWindow(time(0, 0)),
)


def in_blackout(now: datetime,
                windows: tuple[BlackoutWindow, ...] = DEFAULT_WINDOWS) -> BlackoutWindow | None:
    """Return the first window ``now`` falls inside, or None when safe to deploy.

    Args:
        now: The instant to test.
        windows: Blackout windows to check (defaults to noon + midnight, ±5 min).

    Returns:
        The matching :class:`BlackoutWindow`, or None.
    """
    for window in windows:
        if window.contains(now):
            return window
    return None
