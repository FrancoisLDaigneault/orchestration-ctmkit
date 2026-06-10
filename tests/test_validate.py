import json
from pathlib import Path

from ctmkit.validate import validate_tree

FIX = Path(__file__).parent / "fixtures"
SS = FIX / "site-standard.yaml"
SCHEMAS = FIX / "schemas"


def _write(tmp_path, rel, obj):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8")


def test_good_calendar_passes(tmp_path):
    _write(tmp_path, "control-m/0225/development/calendars/0225_HOLYDAY.json",
           {"0225_HOLYDAY": {"Type": "Calendar"}})
    report = validate_tree(tmp_path, site_standard=SS, schemas_dir=SCHEMAS)
    assert report.ok, report.errors


def test_bad_name_fails(tmp_path):
    _write(tmp_path, "control-m/0225/development/calendars/4007_HOLYDAY.json",
           {"4007_HOLYDAY": {"Type": "Calendar"}})
    report = validate_tree(tmp_path, site_standard=SS, schemas_dir=SCHEMAS)
    assert not report.ok
    assert any("0225_" in e for e in report.errors)


def test_filename_must_match_internal_name(tmp_path):
    _write(tmp_path, "control-m/0225/development/calendars/0225_HOLYDAY.json",
           {"0225_OTHER": {"Type": "Calendar"}})
    report = validate_tree(tmp_path, site_standard=SS, schemas_dir=SCHEMAS)
    assert not report.ok
    assert any("filename" in e.lower() for e in report.errors)
