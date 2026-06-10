"""Unit tests for the docs content-hash index + change report (no network)."""
from ctmkit.docs import index


def _write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_sha256_is_stable_and_sensitive():
    assert index.sha256_text("a") == index.sha256_text("a")
    assert index.sha256_text("a") != index.sha256_text("b")


def test_first_run_reports_everything_added(tmp_path):
    _write(tmp_path, "bmc/API/x.md", "one")
    _write(tmp_path, "bmc/API/y.md", "two")
    changes = index.diff_and_update(tmp_path, today="2026-06-10")
    assert sorted(changes.added) == ["bmc/API/x.md", "bmc/API/y.md"]
    assert changes.changed == [] and changes.removed == []


def test_second_run_detects_change_and_removal(tmp_path):
    _write(tmp_path, "bmc/API/x.md", "one")
    _write(tmp_path, "bmc/API/y.md", "two")
    index.diff_and_update(tmp_path, today="2026-06-10")
    _write(tmp_path, "bmc/API/x.md", "ONE-CHANGED")
    (tmp_path / "bmc/API/y.md").unlink()
    changes = index.diff_and_update(tmp_path, today="2026-06-11")
    assert changes.changed == ["bmc/API/x.md"]
    assert changes.removed == ["bmc/API/y.md"]
    assert changes.added == [] and changes.unchanged == 0


def test_changelog_is_prepended_newest_first(tmp_path):
    _write(tmp_path, "bmc/API/x.md", "one")
    c1 = index.diff_and_update(tmp_path, today="2026-06-10")
    index.write_changelog(tmp_path, c1, today="2026-06-10")
    _write(tmp_path, "bmc/API/x.md", "two")
    c2 = index.diff_and_update(tmp_path, today="2026-06-11")
    index.write_changelog(tmp_path, c2, today="2026-06-11")
    text = (tmp_path / index.CHANGELOG_NAME).read_text()
    assert text.index("2026-06-11") < text.index("2026-06-10")
    assert "Documentation updates" in text


def test_index_and_changelog_are_not_self_tracked(tmp_path):
    _write(tmp_path, "bmc/API/x.md", "one")
    index.diff_and_update(tmp_path, today="2026-06-10")
    index.write_changelog(tmp_path, index.DocChanges(added=["bmc/API/x.md"]), today="2026-06-10")
    changes = index.diff_and_update(tmp_path, today="2026-06-11")
    # CHANGELOG.md / .doc-index.json must not appear as tracked docs
    assert changes.added == [] and changes.changed == []
