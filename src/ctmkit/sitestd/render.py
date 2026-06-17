"""Render deployable Control-M SiteStandard + SiteStandardPolicy JSON from the ruleset.

Single source of truth: the regexes live in :mod:`ctmkit.sitestd.rules`; this module projects
them into the Control-M objects you deploy with ``ctm deploy sitestandards``.
"""
from __future__ import annotations

from ctmkit.sitestd import rules

_TEXT_RULES = [
    ("FolderName", rules.FOLDER_RE.pattern, "{CtmServer}#{Prefix}{AppNum}_{Desc}"),
    ("SubFolderName", rules.SUBFOLDER_RE.pattern, "{Prefix}{AppNum}_SF_{Desc}"),
    ("JobName", rules.JOBNAME_RE.pattern, "{Prefix}{AppNum}_{Desc} (no _SF_)"),
    ("Application", rules.APPLICATION_RE.pattern, "{AppNum} - {AppName}"),
    ("DaysKeepActive", rules.DAYSKEEP_RE.pattern, "0 to 31"),
    ("Calendar", rules.CALENDAR_RE.pattern, "!?{Prefix}{AppNum}*"),
]


def site_standard() -> dict:
    """Return the deployable ``BNC-STANDARD`` SiteStandard object."""
    text_rules = [
        {"Type": "Rule:Text", "Property": prop, "RegularExpression": rx, "ErrorMessage": msg}
        for prop, rx, msg in _TEXT_RULES
    ]
    text_rules.append({
        "Type": "Rule:List", "Property": "RunAs", "Operator": "NotIn",
        "Values": sorted(rules.RUNAS_FORBIDDEN),
        "ErrorMessage": "RunAs must not be root/r00t/RES\\SVC_Ctrlm_Tool",
    })
    return {"BNC-STANDARD": {
        "Type": "SiteStandard",
        "Description": "Standards for distributed platform (all applications except 0225)",
        "InternalRules": [
            {"RuleName": "Prefix", "Type": "Rule:Text", "RegularExpression": "^[DIZGA]$"},
            {"RuleName": "AppNum", "Type": "Rule:Text", "RegularExpression": "^\\d{3,4}$"},
        ],
        "Rules": text_rules,
    }}


def ctrlm_admin() -> dict:
    """Return the deployable ``BNC-CTRLM-ADMIN`` SiteStandard (no rules)."""
    return {"BNC-CTRLM-ADMIN": {
        "Type": "SiteStandard",
        "Description": "Control-M administration (0225) — no validation rules",
        "Rules": [],
    }}


def policies() -> dict:
    """Return the SiteStandardPolicy objects that bind the standards to applications."""
    return {
        "BNC-STANDARD-POLICY": {
            "Type": "SiteStandardPolicy", "SiteStandard": "BNC-STANDARD",
            "Description": "Enforce BNC-STANDARD on every application except 0225",
            "Status": "Active", "ErrorLevel": "Error",
            "ApplyOn": {"Server": "*", "Folder": "*"},
        },
        "BNC-CTRLM-ADMIN-POLICY": {
            "Type": "SiteStandardPolicy", "SiteStandard": "BNC-CTRLM-ADMIN",
            "Description": "0225 Control-M admin jobs — no validation rules",
            "Status": "Active", "ErrorLevel": "Default",
            "ApplyOn": {"Server": "*", "Folder": "*#?0225_*"},
        },
    }


def all_objects() -> dict[str, dict]:
    """Map output file stem -> object dict (for `ctmkit audit render`)."""
    return {
        "bnc-standard": site_standard(),
        "bnc-ctrlm-admin": ctrlm_admin(),
        "policies": policies(),
    }
