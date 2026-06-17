"""Audit a Control-M JSON tree against the resolved BNC site standard."""
from __future__ import annotations

from ctmkit.sitestd import rules, standards
from ctmkit.sitestd.rules import PASS, Finding


def audit_tree(obj: dict) -> list[Finding]:
    """Audit every top-level object in a Control-M definitions dict.

    Args:
        obj: Parsed Control-M JSON (``{name: body, ...}``).

    Returns:
        Ordered findings across the whole tree.
    """
    findings: list[Finding] = []
    for name, body in obj.items():
        if isinstance(body, dict):
            findings += _audit_node(name, body)
    return findings


def _audit_node(name: str, body: dict, inherited_application: str = "") -> list[Finding]:
    app_value = body.get("Application") or inherited_application or ""
    app = standards.app_number(app_value, name)
    standard = standards.resolve_for_app(app)

    if not standards.has_rules(standard):
        return [Finding(PASS, "STD_BYPASS", "SiteStandard", standard,
                        f"app {app or '?'}: {standard} imposes no validation rules", node=name)]

    findings: list[Finding] = []
    node_type = body.get("Type", "")
    if node_type == "Folder":
        findings += [rules.folder_name(name), rules.application(body),
                     rules.sub_application(body), rules.description(body)]
        findings += [f for f in (rules.days_keep_active(body), rules.controlm_server(body)) if f]
        findings += rules.calendars(body)
    elif node_type == "SubFolder":
        findings += [rules.sub_folder_name(name), rules.application(body),
                     rules.sub_application(body)]
    elif node_type.startswith("Job"):
        findings += [rules.job_name(name, node_type, body.get("Host", "")),
                     rules.host(body), rules.description(body)]
        findings += [f for f in (rules.run_as(body, app_value),
                                 rules.do_incident(name, body),
                                 rules.days_keep_active(body)) if f]
        findings += rules.events(body)

    for finding in findings:
        if not finding.node:
            finding.node = name

    for child_name, child in body.items():
        if isinstance(child, dict) and "Type" in child:
            findings += _audit_node(child_name, child, inherited_application=app_value)
    return findings
