"""Pure nomenclature rules (no I/O). See design doc §5.

Folders:        [ENV]#D[AppId]_[NAME]      e.g. DEV#D0225_BILLING
Everything else: [AppId]_[NAME]            e.g. 0225_HOLYDAY
NAME is [A-Z0-9_]+ (uppercase); AppId is exactly 4 digits; D is the Distributed letter.
"""
from __future__ import annotations

import re

FOLDER_KINDS = {"folders"}
_NAME = r"[A-Z0-9_]+"


def expected_name(kind: str, stem: str, *, app: str, env_token: str, dist: str) -> str:
    """The internal Control-M Name expected for a file whose stem is `stem`."""
    if kind in FOLDER_KINDS:
        return f"{env_token}#{dist}{app}" + stem[len(f"{dist}{app}"):]
    return stem


def validate_name(name: str, *, kind: str, app: str, env_token: str, dist: str) -> list[str]:
    """Return a list of human-readable problems; empty list means valid."""
    if kind in FOLDER_KINDS:
        pattern = rf"^{re.escape(env_token)}#{re.escape(dist)}{re.escape(app)}_{_NAME}$"
        if not re.fullmatch(pattern, name):
            return [f"folder name {name!r} must match {env_token}#{dist}{app}_<UPPER_NAME>"]
        return []
    pattern = rf"^{re.escape(app)}_{_NAME}$"
    if not re.fullmatch(pattern, name):
        return [f"object name {name!r} must match {app}_<UPPER_NAME>"]
    return []
