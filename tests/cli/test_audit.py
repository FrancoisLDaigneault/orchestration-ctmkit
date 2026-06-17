import json

from typer.testing import CliRunner

from ctmkit.cli import app

runner = CliRunner()

COMPLIANT = {"DEV#D1234_OK": {
    "Type": "Folder", "Application": "1234 - X", "SubApplication": "S", "Description": "d",
    "D1234_J": {"Type": "Job:Command", "Host": "h", "RunAs": "svc", "Description": "d",
                "Variables": [{"DO_INCIDENT": "k"}]}}}
BAD = {"dev#bad": {"Type": "Folder", "Application": "nope", "SubApplication": "", "Description": "",
                   "D1234_J": {"Type": "Job:Command", "Host": "0225_CTM_HOSTGROUP",
                               "RunAs": "root", "Description": "d"}}}


def _write(tmp_path, name, obj):
    p = tmp_path / name
    p.write_text(json.dumps(obj))
    return p


def test_audit_run_passes_compliant(tmp_path):
    _write(tmp_path, "ok.json", COMPLIANT)
    result = runner.invoke(app, ["audit", "run", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "CONFORME" in result.output


def test_audit_run_fails_noncompliant(tmp_path):
    _write(tmp_path, "bad.json", BAD)
    result = runner.invoke(app, ["audit", "run", "--path", str(tmp_path)])
    assert result.exit_code == 1
    assert "NON CONFORME" in result.output


def test_audit_render_writes_standards(tmp_path):
    out = tmp_path / "site-standards"
    result = runner.invoke(app, ["audit", "render", "--out", str(out)])
    assert result.exit_code == 0
    assert (out / "bnc-standard.json").exists()
    assert json.loads((out / "bnc-standard.json").read_text())["BNC-STANDARD"]["Type"] == "SiteStandard"
