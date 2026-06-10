"""Content-hash index for mirrored docs + change reporting.

Records a SHA-256 per document so each crawl can report which docs were added,
changed, or removed — a lightweight "what changed in the vendor docs" feed.
Pure logic + small file I/O; no network.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

INDEX_NAME = ".doc-index.json"
CHANGELOG_NAME = "CHANGELOG.md"
_SKIP = {"README.md", CHANGELOG_NAME}


def sha256_text(text: str) -> str:
    """Return the hex SHA-256 of ``text`` encoded as UTF-8.

    Args:
        text: The text to hash.

    Returns:
        The 64-character hex digest.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class DocChanges:
    """Documents added/changed/removed since the previous index.

    Attributes:
        added: New doc paths (relative to the reference root).
        changed: Doc paths whose content hash changed.
        removed: Doc paths absent since the last run.
        unchanged: Count of docs with identical hashes.
    """

    added: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    unchanged: int = 0

    @property
    def any_change(self) -> bool:
        """True when anything was added, changed, or removed."""
        return bool(self.added or self.changed or self.removed)


def _scan(root: Path) -> dict[str, str]:
    """Map each tracked ``.md`` doc (relative POSIX path) to its content hash."""
    out: dict[str, str] = {}
    for path in sorted(Path(root).rglob("*.md")):
        if path.name in _SKIP:
            continue
        rel = path.relative_to(root).as_posix()
        out[rel] = sha256_text(path.read_text(encoding="utf-8", errors="replace"))
    return out


def load_index(root: Path) -> dict[str, dict]:
    """Load the stored hash index, or an empty dict if none exists.

    Args:
        root: Docs reference root.

    Returns:
        Mapping of relative path to ``{sha256, first_seen, last_changed}``.
    """
    path = Path(root) / INDEX_NAME
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def diff_and_update(root: Path, *, today: str | None = None) -> DocChanges:
    """Compare current docs to the stored index, rewrite the index, return changes.

    Args:
        root: Docs reference root to scan.
        today: ISO date recorded as ``last_changed`` (defaults to today).

    Returns:
        A :class:`DocChanges` describing the delta since the last run.
    """
    root = Path(root)
    today = today or date.today().isoformat()
    prev = load_index(root)
    current = _scan(root)
    changes = DocChanges()
    new_index: dict[str, dict] = {}

    for rel, digest in current.items():
        if rel not in prev:
            changes.added.append(rel)
            new_index[rel] = {"sha256": digest, "first_seen": today, "last_changed": today}
        elif prev[rel].get("sha256") != digest:
            changes.changed.append(rel)
            new_index[rel] = {"sha256": digest,
                              "first_seen": prev[rel].get("first_seen", today),
                              "last_changed": today}
        else:
            changes.unchanged += 1
            new_index[rel] = prev[rel]

    changes.removed = [rel for rel in prev if rel not in current]
    (root / INDEX_NAME).write_text(
        json.dumps(new_index, indent=2, sort_keys=True), encoding="utf-8")
    return changes


def render_changelog_entry(changes: DocChanges, *, today: str | None = None) -> str:
    """Render a single dated changelog entry in markdown.

    Args:
        changes: The changes to render.
        today: ISO date heading (defaults to today).

    Returns:
        A markdown fragment ending with a newline.
    """
    today = today or date.today().isoformat()
    lines = [
        f"## {today}",
        "",
        f"{len(changes.added)} added · {len(changes.changed)} changed · "
        f"{len(changes.removed)} removed · {changes.unchanged} unchanged",
    ]
    for label, items in (("Added", changes.added), ("Changed", changes.changed),
                         ("Removed", changes.removed)):
        if items:
            lines += ["", f"### {label}", *(f"- {item}" for item in items)]
    return "\n".join(lines) + "\n"


def write_changelog(root: Path, changes: DocChanges, *, today: str | None = None) -> None:
    """Prepend a changelog entry to ``CHANGELOG.md`` (newest first).

    No-op when ``changes`` is empty.

    Args:
        root: Docs reference root.
        changes: The changes to record.
        today: ISO date heading (defaults to today).
    """
    if not changes.any_change:
        return
    path = Path(root) / CHANGELOG_NAME
    entry = render_changelog_entry(changes, today=today)
    title = "# Documentation updates\n"
    body = ""
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        title, _, body = existing.partition("\n")
    path.write_text(f"{title}\n{entry}\n{body.lstrip()}", encoding="utf-8")
