"""Render BNC site-standard audit findings."""
from __future__ import annotations

from dataclasses import dataclass, field

from ctmkit.sitestd.rules import FAIL, PASS, WARN, Finding


@dataclass
class Report:
    """A collection of findings + verdict.

    Attributes:
        findings: All findings, in tree order.
    """

    findings: list[Finding] = field(default_factory=list)

    @property
    def failures(self) -> list[Finding]:
        return [f for f in self.findings if f.level == FAIL]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.level == WARN]

    @property
    def ok(self) -> bool:
        """True when there are no blocking (FAIL) findings."""
        return not self.failures

    def summary(self) -> str:
        """One-line verdict, e.g. ``7/8 checks — NON CONFORME (1 blocking)``."""
        passed = sum(1 for f in self.findings if f.level == PASS)
        verdict = "CONFORME" if self.ok else f"NON CONFORME ({len(self.failures)} blocking)"
        return f"{passed}/{len(self.findings)} checks — {verdict}"


def lines(report: Report) -> list[str]:
    """Render findings as plain ``[LEVEL] node prop — value — rule — fix`` lines (testable)."""
    out: list[str] = []
    for f in report.findings:
        base = f"[{f.level}] {f.node} {f.prop} — {f.value!r}"
        if f.level != PASS:
            base += f" — {f.rule_id} — {f.message}"
            if f.fix:
                base += f" (fix: {f.fix})"
        out.append(base)
    out.append(report.summary())
    return out


def render(report: Report) -> None:
    """Pretty-print the report with Rich (FAIL red, WARN yellow, PASS green)."""
    from rich.table import Table

    from ctmkit.cli._console import console

    table = Table(title="BNC site-standard audit", expand=True)
    table.add_column("level")
    table.add_column("object")
    table.add_column("property")
    table.add_column("value/finding")
    colour = {PASS: "green", FAIL: "red", WARN: "yellow"}
    for f in report.findings:
        detail = f.value if f.level == PASS else f"{f.value!r} — {f.message}" + (
            f" (fix: {f.fix})" if f.fix else "")
        table.add_row(f"[{colour[f.level]}]{f.level}[/]", f.node, f"{f.rule_id}:{f.prop}", detail)
    console.print(table)
    style = "green" if report.ok else "red"
    console.print(f"[bold {style}]{report.summary()}[/]")
