from datetime import datetime, time

from ctmkit.policy.blackout import BlackoutWindow, in_blackout


def test_noon_window():
    assert in_blackout(datetime(2026, 6, 10, 12, 3)) is not None
    assert in_blackout(datetime(2026, 6, 10, 11, 57)) is not None
    assert in_blackout(datetime(2026, 6, 10, 12, 6)) is None


def test_midnight_wraps_around():
    assert in_blackout(datetime(2026, 6, 10, 23, 58)) is not None
    assert in_blackout(datetime(2026, 6, 10, 0, 2)) is not None
    assert in_blackout(datetime(2026, 6, 10, 0, 10)) is None


def test_safe_time_is_clear():
    assert in_blackout(datetime(2026, 6, 10, 9, 30)) is None


def test_custom_window_margin():
    windows = (BlackoutWindow(time(6, 0), margin_minutes=10),)
    assert in_blackout(datetime(2026, 6, 10, 6, 8), windows) is not None
    assert in_blackout(datetime(2026, 6, 10, 6, 11), windows) is None
