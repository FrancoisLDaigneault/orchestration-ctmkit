import json

from ctmkit.kpi.emit import append_jsonl, summary_line
from ctmkit.kpi.models import DeployKpi


def _kpi(**kw):
    base = dict(app="0225", env="lab", objects=6, succeeded=6, failed=0,
                duration_s=2.5, ok=True, timestamp="2026-06-10T00:00:00Z")
    base.update(kw)
    return DeployKpi(**base)


def test_to_json_has_fields():
    d = json.loads(_kpi().to_json())
    assert d["app"] == "0225" and d["ok"] is True and d["objects"] == 6


def test_append_jsonl_appends(tmp_path):
    p = tmp_path / "k" / "deploys.jsonl"
    append_jsonl(_kpi(), p)
    append_jsonl(_kpi(env="production", ok=False, failed=1), p)
    lines = p.read_text().strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[1])["env"] == "production"


def test_summary_line():
    line = summary_line(_kpi())
    assert "0225/lab" in line and "ok" in line
