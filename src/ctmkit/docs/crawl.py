"""Full-site crawler for BMC Control-M docs + Control-M GitHub repos.

- BFS each MadCap WebHelp space via the in-page nav links (Cloudflare cleared by
  curl_cffi), staying strictly within the space; external/unrelated links are never
  followed.
- Clean every page to content-only markdown (see clean.py) and lay it out in a
  hierarchy that mirrors the source (prefix-grouped per space).
- Ingest Control-M GitHub repos (doc/markdown files) under the same tree.

    uv run ctmkit-docs-crawl --out docs/reference
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import yaml

from ctmkit.docs.clean import clean_markdown
from ctmkit.docs.index import diff_and_update, write_changelog
from ctmkit.docs.mirror import extract_links, html_to_markdown

DEFAULT_SOURCES = Path(__file__).with_name("crawl_sources.yaml")
DOC_EXT = (".md", ".markdown", ".rst", ".txt")
_SKIP_NAMES = {"requirements.txt", "notes.txt"}


def is_doc_file(f: Path) -> bool:
    """A real doc file, not build/license/dependency noise."""
    if f.suffix.lower() not in DOC_EXT or ".git" in f.parts:
        return False
    if "_static" in f.parts or "node_modules" in f.parts:
        return False
    if f.name.lower() in _SKIP_NAMES or "license" in f.name.lower():
        return False
    return True


# --------------------------------------------------------------------------- #
# pure helpers (unit-tested)
# --------------------------------------------------------------------------- #
def get_title(html: str, fallback: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    if not m:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    if not m:
        return fallback
    title = re.sub(r"<[^>]+>", "", m.group(1))
    title = re.sub(r"\s*[-|–]\s*BMC.*$", "", title).strip()
    return title or fallback


def relpath_for(space: str, name: str) -> str:
    """Map a page name to a hierarchy path mirroring the source structure."""
    if space == "API":
        for pre, folder in {
            "API_CodeRef_": "code-reference",
            "API_Services_": "services",
            "API_Tutorials_": "tutorials",
            "API_Mng_": "managing",
        }.items():
            if name.startswith(pre):
                return f"{folder}/{name[len(pre):]}.md"
        return f"{name}.md"
    if space == "K8S":
        return f"{name[4:] if name.startswith('K8S_') else name}.md"
    if space == "9.0.22":
        if name.startswith("AI_"):
            return f"application-integrator/{name[3:]}.md"
        return f"{name}.md"
    return f"{name}.md"


def page_name(url: str) -> str:
    return url.rsplit("/", 1)[-1].rsplit(".", 1)[0]


# --------------------------------------------------------------------------- #
# crawl (network)
# --------------------------------------------------------------------------- #
def _session(impersonate: str):
    from curl_cffi import requests as cr

    return cr.Session(impersonate=impersonate)


def crawl_space(sess, space: str, index_url: str, allow_prefix: str,
                out_dir: Path, max_pages: int, delay: float) -> list[tuple[str, object]]:
    queue = [index_url]
    visited: set[str] = set()
    rows: list[tuple[str, object]] = []
    toc: list[tuple[str, str]] = []
    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            r = sess.get(url, timeout=60)
            if r.status_code != 200 or "Just a moment" in r.text:
                rows.append((url, r.status_code))
                continue
            name = page_name(url)
            title = get_title(r.text, name)
            body = clean_markdown(html_to_markdown(r.text))
            if not body.lstrip().startswith("# "):  # only add a title if the page lacks an H1
                body = f"# {title}\n\n{body}"
            rel = relpath_for(space, name)
            dest = out_dir / "bmc" / space / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f"<!-- source: {url} -->\n\n{body}", encoding="utf-8")
            toc.append((title, f"bmc/{space}/{rel}"))
            rows.append((url, "ok"))
            for link in extract_links(r.text, url, [allow_prefix]):
                if "/Resources/" not in link and link not in visited and link not in queue:
                    queue.append(link)
        except Exception as exc:  # noqa: BLE001
            rows.append((url, f"ERR {str(exc)[:50]}"))
        time.sleep(delay)

    toc.sort()
    toc_md = f"# {space} — table of contents\n\n" + "".join(
        f"- [{t}]({p})\n" for t, p in toc
    )
    (out_dir / "bmc" / space / "_toc.md").write_text(toc_md, encoding="utf-8")
    return rows


def ingest_repo(url: str, out_dir: Path) -> int:
    name = url.rstrip("/").rsplit("/", 1)[-1]
    tmp = Path(tempfile.mkdtemp())
    n = 0
    try:
        subprocess.run(["git", "clone", "--depth", "1", url, str(tmp)],
                       check=True, capture_output=True, timeout=300)
        for f in tmp.rglob("*"):
            if f.is_file() and is_doc_file(f):
                rel = f.relative_to(tmp)
                dest = out_dir / "github" / name / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(clean_markdown(f.read_text(encoding="utf-8", errors="replace")),
                                encoding="utf-8")
                n += 1
    except Exception as exc:  # noqa: BLE001
        print(f"  repo {name}: ERR {exc}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return n


def ingest_file(sess, url: str, out_dir: Path) -> bool:
    raw = (url.replace("https://github.com/", "https://raw.githubusercontent.com/")
              .replace("/blob/", "/"))
    try:
        r = sess.get(raw, timeout=60)
        if r.status_code != 200:
            return False
        rel = raw.split("raw.githubusercontent.com/", 1)[1]
        dest = out_dir / "github" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(clean_markdown(r.text), encoding="utf-8")
        return True
    except Exception:
        return False


def ingest_article(sess, name: str, url: str, out_dir: Path) -> str:
    """Fetch one documentation article and save it as cleaned markdown.

    Args:
        sess: HTTP session.
        name: Output stem under ``bmc/`` (may include subdirs).
        url: Article URL.
        out_dir: Reference root.

    Returns:
        ``"ok"``, ``"js-gated (needs a browser)"``, or a ``"FAIL ..."`` string.
    """
    try:
        r = sess.get(url, timeout=60)
        if r.status_code != 200 or "Just a moment" in r.text:
            return f"FAIL (HTTP {r.status_code})"
        body = clean_markdown(html_to_markdown(r.text))
        if len(body) < 200:
            return "js-gated (needs a browser)"
        dest = out_dir / "bmc" / f"{name}.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f"<!-- source: {url} -->\n\n{body}", encoding="utf-8")
        return "ok"
    except Exception as exc:  # noqa: BLE001
        return f"FAIL ({str(exc)[:40]})"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Crawl BMC docs + Control-M GitHub repos.")
    ap.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    ap.add_argument("--out", type=Path, default=Path("docs/reference"))
    ap.add_argument("--only", choices=["bmc", "github", "articles", "index"],
                    help="limit to one source kind")
    ap.add_argument("--max", type=int, help="override max pages per space (for bounded runs)")
    args = ap.parse_args(argv)

    cfg = yaml.safe_load(args.sources.read_text(encoding="utf-8"))
    sess = _session(cfg.get("impersonate", "chrome124"))
    delay = float(cfg.get("delay_seconds", 0.5))
    max_pages = args.max or int(cfg.get("max_pages_per_space", 2000))
    args.out.mkdir(parents=True, exist_ok=True)

    if args.only in (None, "bmc"):
        for sp in cfg.get("spaces", []):
            print(f"\n=== crawl {sp['name']} ===", flush=True)
            rows = crawl_space(sess, sp["name"], sp["index"], sp["allow_prefix"],
                               args.out, max_pages, delay)
            ok = sum(1 for _, s in rows if s == "ok")
            print(f"  {sp['name']}: {ok}/{len(rows)} pages", flush=True)

    if args.only in (None, "github"):
        print("\n=== github repos ===", flush=True)
        for repo in cfg.get("repos", []):
            print(f"  {repo}: {ingest_repo(repo, args.out)} doc files", flush=True)
        for f in cfg.get("files", []):
            print(f"  file {f}: {'ok' if ingest_file(sess, f, args.out) else 'FAIL'}", flush=True)

    if args.only in (None, "articles"):
        print("\n=== articles ===", flush=True)
        for art in cfg.get("articles", []):
            print(f"  {art['name']}: {ingest_article(sess, art['name'], art['url'], args.out)}",
                  flush=True)

    # refresh the content-hash index + change report on every run
    changes = diff_and_update(args.out)
    write_changelog(args.out, changes)
    print(f"\ndoc changes: +{len(changes.added)} ~{len(changes.changed)} "
          f"-{len(changes.removed)} ({changes.unchanged} unchanged)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
