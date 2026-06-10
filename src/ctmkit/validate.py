"""Validate a manifests tree: schema + nomenclature + filename<->Name consistency.

Path convention: control-m/<app>/<env>/<kind>/<stem>.json
Works on a whole repo OR a subtree (any path that still contains a control-m/ segment).
Deploy descriptors and not-yet-schema'd kinds are skipped.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from ctmkit.config import load_site_standard
from ctmkit.naming import expected_name, validate_name
from ctmkit.schema import KNOWN_KINDS, validate_object

_ENV_DIRS = {"development", "staging", "production", "lab"}
_SKIP_KINDS = {"deploy_descriptor"}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _context(path: Path):
    """Return (app, env, kind, stem) from a .../control-m/<app>/<env>/<kind>/<stem>.json path."""
    parts = path.parts
    i = parts.index("control-m")
    app, env, kind = parts[i + 1], parts[i + 2], parts[i + 3]
    return app, env, kind, path.stem


def validate_tree(root: Path, *, site_standard: Path, schemas_dir: Path) -> Report:
    ss = load_site_standard(site_standard)
    report = Report()
    for path in sorted(Path(root).rglob("*.json")):
        if "control-m" not in path.parts:
            continue
        try:
            app, env, kind, stem = _context(path)
        except (ValueError, IndexError):
            continue
        if env not in _ENV_DIRS or kind in _SKIP_KINDS or kind not in KNOWN_KINDS:
            continue

        env_token = ss.env_token(env)
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            report.errors.append(f"{path}: invalid JSON: {exc}")
            continue

        for e in validate_object(obj, kind, schemas_dir):
            report.errors.append(f"{path}: {e}")

        if len(obj) != 1:
            report.errors.append(f"{path}: must contain exactly one object (got {len(obj)})")
            continue
        name = next(iter(obj))

        for e in validate_name(name, kind=kind, app=app,
                               env_token=env_token, dist=ss.distributed_letter):
            report.errors.append(f"{path}: {e}")

        want = expected_name(kind, stem, app=app, env_token=env_token,
                             dist=ss.distributed_letter)
        if name != want:
            report.errors.append(
                f"{path}: filename implies Name {want!r} but object is {name!r}")
    return report
