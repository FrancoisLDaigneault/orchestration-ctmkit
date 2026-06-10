"""Aggressive, content-only cleaning for mirrored docs.

Strips invisible/control characters, MadCap/WebHelp nav chrome, "Copy" buttons,
javascript: links, images, and date/copyright footers — then normalises whitespace.
Pure functions, unit-tested, no network.
"""
from __future__ import annotations

import re
import unicodedata

# zero-width / BOM / word-joiner / soft-hyphen -> removed; NBSP -> normal space
_INVISIBLE = dict.fromkeys(
    map(ord, "​‌‍⁠﻿­‎‏"), None
)

# whole lines that are pure navigation/UI chrome
_NAV_NOISE = {
    "Skip To Main Content", "Account Settings", "Logout", "placeholder",
    "Filter:", "Submit Search", "Submit", "Search", "Home", "Everything",
    "Was this helpful?", "Send feedback", "Print", "Expand all", "Collapse all",
}

_DATE_FOOTER = re.compile(
    r"(?i)(©|copyright\b|all rights reserved|last (updated|modified|published)"
    r"|©\s*\d{4}|\bBMC Software\b.*\d{4})"
)

# trailing junk: cut the page here if we hit one of these markers on its own line
_CUT_AFTER = re.compile(r"(?i)^\s*(related (topics|information)|parent topic|©|copyright)\b")

# element blocks whose *content* must be removed before any markdown conversion
_HTML_NOISE = re.compile(
    r"(?is)<(script|style|noscript|head|svg|template|iframe)\b[^>]*>.*?</\1\s*>"
)


def strip_html_blocks(html: str) -> str:
    """Remove script/style/head/svg/iframe element blocks, content included.

    ``markdownify``'s ``strip`` only unwraps tags (keeping their inner text), which
    leaks JS/CSS into the output for non-WebHelp pages. Deleting the blocks first
    guarantees a content-only conversion.

    Args:
        html: Raw HTML.

    Returns:
        HTML with noise element blocks removed.
    """
    return _HTML_NOISE.sub(" ", html)


def strip_invisible(text: str) -> str:
    text = text.translate(_INVISIBLE).replace(" ", " ")
    # drop remaining control chars except tab/newline
    return "".join(c for c in text if c in "\n\t" or unicodedata.category(c)[0] != "C")


def clean_markdown(md_text: str, *, drop_dates: bool = True) -> str:
    t = strip_invisible(md_text)

    # MadCap "Copy" code buttons + any javascript: links -> keep visible text only
    t = re.sub(r"\[Copy\]\(javascript:[^)]*\)", "", t)
    t = re.sub(r"\[([^\]]*)\]\(javascript:[^)]*\)", r"\1", t)
    # drop images entirely (assets, not content)
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)
    # drop the breadcrumb line
    t = re.sub(r"(?m)^\s*You are here:.*$", "", t)
    # nav chrome that survives as markdown links, e.g. [Skip To Main Content](#)
    t = re.sub(
        r"\[(?:Skip To Main Content|Account Settings|Logout|Submit Search|Search)\]\([^)]*\)",
        "", t,
    )
    # collapse links that point nowhere useful: [text]() -> text
    t = re.sub(r"\[([^\]]+)\]\(\s*\)", r"\1", t)

    out: list[str] = []
    for raw in t.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if s in _NAV_NOISE:
            continue
        if drop_dates and _DATE_FOOTER.search(s):
            continue
        if _CUT_AFTER.match(s):
            break  # everything past here is trailing nav/legal
        out.append(line)

    text = "\n".join(out)
    text = re.sub(r"[ \t]+\n", "\n", text)        # trailing ws
    text = re.sub(r"\n{3,}", "\n\n", text)         # >=3 blank lines -> 1
    return text.strip() + "\n"


def front_matter(title: str, source_url: str) -> str:
    title = title.replace('"', "'").strip()
    return f"# {title}\n\n<!-- source: {source_url} -->\n\n"
