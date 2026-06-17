"""Site standards and per-application resolution.

``BNC-STANDARD`` governs every application **except** 0225; ``BNC-CTRLM-ADMIN`` governs the 0225
Control-M admin application and imposes **no** validation rules.
"""
from __future__ import annotations

import re

BNC_STANDARD = "BNC-STANDARD"
BNC_CTRLM_ADMIN = "BNC-CTRLM-ADMIN"

_NO_RULE_APPS = {"0225"}
_APP_FROM_APPLICATION = re.compile(r"^(\d{3,4}) - ")
_APP_FROM_FOLDER = re.compile(r"#[DIZGA](\d{3,4})_")


def app_number(application_value: str = "", name: str = "") -> str | None:
    """Resolve the application number from an ``Application`` value or object name.

    Args:
        application_value: The object's ``Application`` (``"{num} - {name}"``).
        name: The object name (folder names embed ``#{Prefix}{AppNum}_``).

    Returns:
        The 3-4 digit app number, or None.
    """
    match = _APP_FROM_APPLICATION.match(application_value or "")
    if match:
        return match.group(1)
    match = _APP_FROM_FOLDER.search(name or "")
    if match:
        return match.group(1)
    return None


def resolve_for_app(app: str | None) -> str:
    """Return the site standard that governs ``app``."""
    return BNC_CTRLM_ADMIN if app in _NO_RULE_APPS else BNC_STANDARD


def has_rules(standard: str) -> bool:
    """Whether ``standard`` imposes validation rules."""
    return standard == BNC_STANDARD
