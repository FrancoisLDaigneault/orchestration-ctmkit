"""Unit tests for content-only cleaning (no network)."""
from ctmkit.docs import clean


def test_strip_invisible_removes_zero_width_and_normalises_nbsp():
    raw = "a​b c﻿­d"
    assert clean.strip_invisible(raw) == "ab cd"


def test_clean_drops_copy_buttons_images_and_breadcrumb():
    md = (
        "You are here: A > B\n\n"
        "# Title\n\n"
        "[Copy](javascript:void(0);)\n\n"
        "![diagram](images/x.png)\n\n"
        "Real content.\n"
    )
    out = clean.clean_markdown(md)
    assert "You are here" not in out
    assert "Copy" not in out
    assert "images/x.png" not in out
    assert "# Title" in out and "Real content." in out


def test_clean_drops_date_and_copyright_footer():
    md = "Body text.\n\nCopyright BMC Software 2026\nLast updated: June 2026\n"
    out = clean.clean_markdown(md)
    assert "Body text." in out
    assert "Copyright" not in out
    assert "Last updated" not in out


def test_clean_collapses_blank_lines():
    assert clean.clean_markdown("a\n\n\n\n\nb\n") == "a\n\nb\n"


def test_javascript_link_keeps_text():
    assert "click" in clean.clean_markdown("[click](javascript:foo())")
    assert "javascript" not in clean.clean_markdown("[click](javascript:foo())")


def test_chrome_links_are_removed():
    out = clean.clean_markdown("# T\n\n[Skip To Main Content](#)\n\nBody.\n")
    assert "Skip To Main Content" not in out
    assert "Body." in out
