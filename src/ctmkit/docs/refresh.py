"""Incremental docs refresh — re-fetch only pages the server reports as modified.

Each mirrored ``.md`` records its source URL. For each, we issue a conditional GET
(``If-Modified-Since`` = the local file's mtime); a ``304`` means unchanged (skipped), a
``200`` means re-fetch + rewrite. Pair with the hash-index diff for the change report.
"""
from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from email.utils import formatdate
from pathlib import Path

_SOURCE_RE = re.compile(r"<!--\s*source:\s*(\S+)\s*-->")
_SKIP = {"README.md", "CHANGELOG.md"}


@dataclass
class RefreshResult:
    """Outcome of an incremental refresh.

    Attributes:
        updated: Pages the server returned 200 for (re-fetched + rewritten).
        unchanged: Pages the server returned 304 for (skipped).
        errors: Pages that failed (blocked / network / non-2xx).
    """

    updated: int = 0
    unchanged: int = 0
    errors: int = 0


def source_url(md_text: str) -> str | None:
    """Extract the ``<!-- source: URL -->`` URL from a mirrored markdown file.

    Args:
        md_text: File contents.

    Returns:
        The URL, or None if absent.
    """
    match = _SOURCE_RE.search(md_text)
    return match.group(1) if match else None


def if_modified_since(path: Path) -> str:
    """Return an HTTP-date string for ``path``'s mtime (for ``If-Modified-Since``).

    Args:
        path: The local file.

    Returns:
        An RFC-1123 date string, e.g. ``"Wed, 10 Jun 2026 00:00:00 GMT"``.
    """
    return formatdate(Path(path).stat().st_mtime, usegmt=True)


def refresh(out_dir: Path, session, *, clean_fn: Callable[[str], str]) -> RefreshResult:
    """Conditionally re-fetch every mirrored page; rewrite only the modified ones.

    Args:
        out_dir: Docs reference root to refresh.
        session: An HTTP session exposing ``get(url, headers=..., timeout=...)``.
        clean_fn: Converts fetched HTML to the cleaned markdown body.

    Returns:
        A :class:`RefreshResult`.
    """
    result = RefreshResult()
    for path in sorted(Path(out_dir).rglob("*.md")):
        if path.name in _SKIP:
            continue
        url = source_url(path.read_text(encoding="utf-8", errors="replace"))
        if not url:
            continue
        try:
            resp = session.get(url, headers={"If-Modified-Since": if_modified_since(path)},
                               timeout=60)
        except Exception:  # noqa: BLE001 - count and continue
            result.errors += 1
            continue
        if resp.status_code == 304:
            result.unchanged += 1
        elif resp.status_code == 200 and "Just a moment" not in resp.text:
            path.write_text(f"<!-- source: {url} -->\n\n{clean_fn(resp.text)}\n", encoding="utf-8")
            result.updated += 1
        else:
            result.errors += 1
    return result
