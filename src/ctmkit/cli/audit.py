"""`ctmkit audit` surface: BNC site-standard compliance + deployable standard rendering."""
from __future__ import annotations

import json
from pathlib import Path

import typer

from ctmkit.cli._console import success
from ctmkit.sitestd import render as render_std
from ctmkit.sitestd.engine import audit_tree
from ctmkit.sitestd.report import Report
from ctmkit.sitestd.report import render as render_report

app = typer.Typer(no_args_is_help=True, help="BNC site-standard compliance.")


def _is_ctm_tree(obj: object) -> bool:
    return isinstance(obj, dict) and any(
        isinstance(v, dict) and "Type" in v for v in obj.values())


@app.command()
def run(
    path: Path = typer.Option(..., "--path", help="A Control-M JSON file or a directory tree."),
) -> None:
    """Audit Control-M JSON against the resolved BNC site standard (0225 is rule-exempt)."""
    files = [path] if path.is_file() else sorted(path.rglob("*.json"))
    findings = []
    for fpath in files:
        try:
            obj = json.loads(fpath.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if _is_ctm_tree(obj):
            findings += audit_tree(obj)
    report = Report(findings)
    render_report(report)
    raise typer.Exit(0 if report.ok else 1)


@app.command()
def render(
    out: Path = typer.Option(Path("config/site-standards"), "--out",
                             help="Directory to write the SiteStandard/Policy JSON."),
) -> None:
    """Generate deployable BNC-STANDARD / BNC-CTRLM-ADMIN SiteStandard + Policy JSON."""
    out.mkdir(parents=True, exist_ok=True)
    for stem, obj in render_std.all_objects().items():
        (out / f"{stem}.json").write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    success(f"rendered site standards to {out}")
