"""Mirror BMC Control-M docs to clean markdown.

Reads a ``sources.yaml`` describing explicit pages + BFS seeds, fetches each page
with a browser-impersonating client (clears Cloudflare), converts the main content
to markdown, and writes one ``.md`` per page under an output tree.

Designed to be run periodically (cron / GitHub Actions) to refresh the offline copy.

    uv run ctmkit-docs --sources src/ctmkit/docs/sources.yaml --out docs/reference/bmc
"""
from __future__ import annotations

import argparse
import re
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin

import yaml

DEFAULT_SOURCES = Path(__file__).with_name("sources.yaml")


# --------------------------------------------------------------------------- #
# HTML helpers (pure, unit-testable, no network)
# --------------------------------------------------------------------------- #
class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)


def extract_links(html: str, base_url: str, allow_prefixes: list[str]) -> list[str]:
    """Absolute, de-fragmented .htm links under one of ``allow_prefixes``."""
    p = _LinkParser()
    p.feed(html)
    out: list[str] = []
    seen: set[str] = set()
    for href in p.hrefs:
        if href.startswith(("javascript:", "mailto:", "#")):
            continue
        absu = urldefrag(urljoin(base_url, href))[0]
        if not absu.lower().endswith((".htm", ".html")):
            continue
        if not any(absu.startswith(pref) for pref in allow_prefixes):
            continue
        if absu not in seen:
            seen.add(absu)
            out.append(absu)
    return out


def html_to_markdown(html: str) -> str:
    """Convert a BMC WebHelp page to markdown, trimming nav chrome."""
    from markdownify import markdownify as md  # local import: optional at test time

    from ctmkit.docs.clean import strip_html_blocks

    html = strip_html_blocks(html)  # delete script/style/head content, not just unwrap
    i = html.find("You are here")
    body = html[i:] if i != -1 else html
    text = md(body, heading_style="ATX", strip=["script", "style", "nav"])
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def slug_for(url: str) -> tuple[str, str]:
    """Return (space, name) used to lay out the output tree."""
    # .../supportu/<space>/.../Documentation/<Page>.htm
    parts = url.split("/supportu/", 1)
    space = "misc"
    if len(parts) == 2:
        space = parts[1].split("/", 1)[0]
    name = url.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return space, name


# --------------------------------------------------------------------------- #
# Fetch + crawl (network)
# --------------------------------------------------------------------------- #
def _session(impersonate: str):
    from curl_cffi import requests as cr  # local import so tests don't need it

    return cr.Session(impersonate=impersonate)


def mirror(sources: dict, out_dir: Path) -> list[tuple[str, object, int, str]]:
    impersonate = sources.get("impersonate", "chrome124")
    max_pages = int(sources.get("max_pages", 60))
    delay = float(sources.get("delay_seconds", 1.0))
    allow = list(sources.get("allow_prefixes", []))
    explicit = list(sources.get("pages", []))
    seeds = list(sources.get("seeds", []))

    sess = _session(impersonate)
    queue: list[str] = list(dict.fromkeys(explicit + seeds))
    explicit_set = set(explicit)
    visited: set[str] = set()
    rows: list[tuple[str, object, int, str]] = []

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            r = sess.get(url, timeout=60)
            blocked = "Just a moment" in r.text
            if r.status_code == 200 and not blocked:
                body = html_to_markdown(r.text)
                space, name = slug_for(url)
                dest = out_dir / space / f"{name}.md"
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(f"<!-- source: {url} -->\n\n{body}\n", encoding="utf-8")
                rows.append((url, r.status_code, len(body), "ok"))
                # only expand the crawl from explicit pages / seeds, depth-1 style,
                # bounded by allow_prefixes + max_pages
                for link in extract_links(r.text, url, allow):
                    if link not in visited and link not in queue:
                        queue.append(link)
            else:
                rows.append((url, r.status_code, len(r.text), "BLOCKED" if blocked else "skip"))
        except Exception as exc:  # noqa: BLE001 - report and continue
            rows.append((url, "ERR", 0, str(exc)[:70]))
        time.sleep(delay)

    # make sure every explicit page actually landed
    landed = {u for u, code, _, note in rows if note == "ok"}
    for u in explicit_set - landed:
        rows.append((u, "MISS", 0, "explicit page not mirrored"))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Mirror BMC Control-M docs to markdown.")
    ap.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    ap.add_argument("--out", type=Path, default=Path("docs/reference/bmc"))
    args = ap.parse_args(argv)

    sources = yaml.safe_load(args.sources.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    rows = mirror(sources, args.out)

    width = max((len(u) for u, *_ in rows), default=10)
    ok = sum(1 for *_, note in rows if note == "ok")
    for url, code, n, note in rows:
        print(f"  {url.ljust(width)}  {str(code).rjust(4)}  {str(n).rjust(7)}  {note}")
    print(f"\n{ok}/{len(rows)} pages mirrored -> {args.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
