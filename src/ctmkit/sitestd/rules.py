"""BNC-STANDARD rules as pure predicates returning Findings.

Each predicate inspects one Control-M node (folder / sub-folder / job) and returns a
:class:`Finding` (PASS / FAIL / WARN) or None when the rule does not apply. Regexes are taken
verbatim from the BNC-STANDARD site standard.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

FOLDER_RE = re.compile(r"^[A-Z0-9_-]+#[DIZGA]\d{3,4}_[A-Z0-9_-]+$")
SUBFOLDER_RE = re.compile(r"^[DIZGA]\d{3,4}_SF_[A-Z0-9_-]+$")
JOBNAME_RE = re.compile(r"^[DIZGA]\d{3,4}_[A-Z0-9_-]+$")
JOBNAME_AS400_RE = re.compile(r"^[A-Z0-9_-]{1,10}$")
APPLICATION_RE = re.compile(r"^\d{3,4} - .+$")
DAYSKEEP_RE = re.compile(r"^([0-9]|[12][0-9]|3[01])$")
CALENDAR_RE = re.compile(r"^!?[DIZGA]\d{3,4}[A-Z0-9_-]*$")

RUNAS_FORBIDDEN = {"root", "r00t", "RES\\SVC_Ctrlm_Tool"}
HOST_EXCLUDE_RE = [re.compile(p) for p in (
    r"^lr.*ccctrlmem", r"^lr.*ccctrlmctm", r"^lr.*ccctrlmarch",
    r"^0225_EM_HOSTGROUP$", r"^0225_CTM_HOSTGROUP$", r"^0225_CTM_MIDNIGHT_HOSTGROUP$",
)]
IO_HOST_PREFIXES = ("iopap", "iodap", "ioeap")
KNOWN_SERVERS = {"DEV", "DEV_MIDNIGHT", "QA", "QA_MIDNIGHT", "PROD", "PROD_MIDNIGHT"}

PASS, FAIL, WARN = "PASS", "FAIL", "WARN"


@dataclass
class Finding:
    """A single rule outcome.

    Attributes:
        level: ``PASS`` / ``FAIL`` / ``WARN``.
        rule_id: The rule identifier (e.g. ``R06_RUNAS``).
        prop: The property checked.
        value: The observed value.
        message: Human-readable explanation (for FAIL/WARN).
        fix: Suggested correction.
        node: The object name the finding belongs to.
    """

    level: str
    rule_id: str
    prop: str
    value: str
    message: str = ""
    fix: str = ""
    node: str = ""

    @property
    def ok(self) -> bool:
        return self.level != FAIL


def _pass(rule_id: str, prop: str, value: str) -> Finding:
    return Finding(PASS, rule_id, prop, value)


# --- Folder / SubFolder -------------------------------------------------------
def folder_name(name: str) -> Finding:
    """R01 — ``{CtmServer}#{Prefix}{AppNum}_{Desc}``."""
    if FOLDER_RE.fullmatch(name):
        return _pass("R01_FOLDER_NAME", "FolderName", name)
    return Finding(FAIL, "R01_FOLDER_NAME", "FolderName", name,
                   "must match {CtmServer}#{Prefix}{AppNum}_{Desc}",
                   "e.g. DEV#D1234_BATCH_DAILY (uppercase, '#', prefix D/I/Z/G/A, 3-4 digit app)")


def sub_folder_name(name: str) -> Finding:
    """R09 — ``{Prefix}{AppNum}_SF_{Desc}``."""
    if SUBFOLDER_RE.fullmatch(name):
        return _pass("R09_SUBFOLDER_NAME", "SubFolderName", name)
    return Finding(FAIL, "R09_SUBFOLDER_NAME", "SubFolderName", name,
                   "must contain _SF_ after {Prefix}{AppNum}", "e.g. D1234_SF_STEP1")


def application(body: dict) -> Finding:
    """R02 — ``{AppNum} - {AppName}`` (required)."""
    value = body.get("Application", "")
    if APPLICATION_RE.fullmatch(value):
        return _pass("R02_APPLICATION", "Application", value)
    return Finding(FAIL, "R02_APPLICATION", "Application", value,
                   "must be '{AppNum} - {AppName}'", "e.g. '1234 - Gestion Comptes'")


def sub_application(body: dict) -> Finding:
    """R03 — SubApplication required, non-empty."""
    value = body.get("SubApplication", "")
    if value.strip():
        return _pass("R03_SUBAPPLICATION", "SubApplication", value)
    return Finding(FAIL, "R03_SUBAPPLICATION", "SubApplication", value,
                   "is required and must not be empty", "set a sub-application label")


def description(body: dict) -> Finding:
    """R04 — Description required, non-empty."""
    value = body.get("Description", "")
    if value.strip():
        return _pass("R04_DESCRIPTION", "Description", value)
    return Finding(FAIL, "R04_DESCRIPTION", "Description", value,
                   "is required and must not be empty", "add a Description")


def days_keep_active(body: dict) -> Finding | None:
    """R11 — DaysKeepActive 0..31 (when present)."""
    if "DaysKeepActive" not in body:
        return None
    value = str(body["DaysKeepActive"])
    if DAYSKEEP_RE.fullmatch(value):
        return _pass("R11_DAYSKEEPACTIVE", "DaysKeepActive", value)
    return Finding(FAIL, "R11_DAYSKEEPACTIVE", "DaysKeepActive", value,
                   "must be between 0 and 31", "set 0-31 (max 31)")


def controlm_server(body: dict) -> Finding | None:
    """R14 — ControlmServer should be a known value (WARNING)."""
    value = body.get("ControlmServer")
    if value is None:
        return None
    if value in KNOWN_SERVERS:
        return _pass("R14_SERVER", "ControlmServer", value)
    return Finding(WARN, "R14_SERVER", "ControlmServer", value,
                   "not a known Control-M/Server", "expected one of DEV/QA/PROD(/_MIDNIGHT)")


def calendars(body: dict) -> list[Finding]:
    """R12 — rule-based calendar names ``!?{Prefix}{AppNum}…``."""
    out: list[Finding] = []
    for cal in body.get("RuleBasedCalendars", []) or []:
        if CALENDAR_RE.fullmatch(cal):
            out.append(_pass("R12_CALENDAR", "RuleBasedCalendars", cal))
        else:
            out.append(Finding(FAIL, "R12_CALENDAR", "RuleBasedCalendars", cal,
                               "must match !?{Prefix}{AppNum}… (uppercase)", "e.g. D1234_WDY"))
    return out


# --- Jobs ---------------------------------------------------------------------
def job_name(name: str, job_type: str, host: str) -> Finding:
    """R07 / R08 — job name, AS/400 vs standard vs IO-host."""
    if "_SF_" in name:
        return Finding(FAIL, "R07_JOB_NAME", "JobName", name,
                       "job names must not contain _SF_", "drop the _SF_ marker")
    if job_type == "Job:OS400 Multiple Commands":
        if JOBNAME_AS400_RE.fullmatch(name):
            return _pass("R08_JOB_NAME_AS400", "JobName", name)
        return Finding(FAIL, "R08_JOB_NAME_AS400", "JobName", name,
                       "AS/400 job name: max 10 chars, uppercase/digits/_-", "e.g. I5678_RPRT")
    if host.startswith(IO_HOST_PREFIXES):
        return _pass("R07_JOB_NAME", "JobName", name)  # IO hosts: no pattern constraint
    if JOBNAME_RE.fullmatch(name):
        return _pass("R07_JOB_NAME", "JobName", name)
    return Finding(FAIL, "R07_JOB_NAME", "JobName", name,
                   "must match {Prefix}{AppNum}_{Desc} (uppercase, no _SF_)", "e.g. D1234_EXTRACT")


def host(body: dict) -> Finding:
    """R05 — Host required, not an infra host/hostgroup."""
    value = body.get("Host", "")
    if not value:
        return Finding(FAIL, "R05_HOST", "Host", value, "is required", "set an application host")
    if any(rx.match(value) for rx in HOST_EXCLUDE_RE):
        return Finding(FAIL, "R05_HOST", "Host", value,
                       "infra host/hostgroup reserved to 0225 (BNC-CTRLM-ADMIN)",
                       "use an application host, not Control-M infrastructure")
    return _pass("R05_HOST", "Host", value)


def run_as(body: dict, application_value: str) -> Finding | None:
    """R06 — RunAs not root-like; skipped for app '4007 - MFT'."""
    if application_value == "4007 - MFT":
        return None
    value = body.get("RunAs", "")
    if not value:
        return Finding(FAIL, "R06_RUNAS", "RunAs", value, "is required", "set a service account")
    if value in RUNAS_FORBIDDEN:
        return Finding(FAIL, "R06_RUNAS", "RunAs", value,
                       "root/r00t/RES\\SVC_Ctrlm_Tool are forbidden", "use a service account")
    return _pass("R06_RUNAS", "RunAs", value)


def _job_variables(body: dict) -> set[str]:
    names: set[str] = set()
    for var in body.get("Variables", []) or []:
        if isinstance(var, dict):
            names.update(var.keys())
    return names


def do_incident(name: str, body: dict) -> Finding | None:
    """R10 — DO_INCIDENT required unless name has '#', '_#_' or '_SF_'."""
    if "#" in name or "_#_" in name or "_SF_" in name:
        return None
    if "DO_INCIDENT" in _job_variables(body):
        return _pass("R10_DO_INCIDENT", "Variables.DO_INCIDENT", "present")
    return Finding(FAIL, "R10_DO_INCIDENT", "Variables.DO_INCIDENT", "absent",
                   "DO_INCIDENT variable is mandatory", 'add {"DO_INCIDENT": "<key>"}')


def events(body: dict) -> list[Finding]:
    """R13 — event names must not contain a wildcard ``*``."""
    out: list[Finding] = []
    for key in ("eventsToAdd", "eventsToWaitFor"):
        block = body.get(key) or {}
        for ev in block.get("Events", []) or []:
            value = ev.get("Event", "") if isinstance(ev, dict) else str(ev)
            if "*" in value:
                out.append(Finding(FAIL, "R13_EVENTS", "Events", value,
                                   "wildcard '*' not allowed in event names", "use an exact name"))
            else:
                out.append(_pass("R13_EVENTS", "Events", value))
    return out
