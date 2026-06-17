from ctmkit.sitestd import standards
from ctmkit.sitestd.engine import audit_tree
from ctmkit.sitestd.report import Report
from ctmkit.sitestd.rules import FAIL, PASS

COMPLIANT = {
    "DEV#D1234_BATCH_DAILY": {
        "Type": "Folder", "Application": "1234 - Gestion", "SubApplication": "Batch",
        "ControlmServer": "DEV", "Description": "daily batch", "DaysKeepActive": "3",
        "RuleBasedCalendars": ["D1234_WDY"],
        "D1234_EXTRACT": {
            "Type": "Job:Command", "Host": "appHost", "RunAs": "svc_1234",
            "Description": "extract", "Variables": [{"DO_INCIDENT": "1234_EXTRACT"}],
        },
    }
}

ADMIN_0225 = {
    "DEV#D0225_CTM_MAINT": {
        "Type": "Folder", "Application": "0225 - Control-M", "SubApplication": "Admin",
        "ControlmServer": "DEV", "Description": "maintenance",
        "D0225_CLEAN": {"Type": "Job:Command", "Host": "0225_CTM_HOSTGROUP", "RunAs": "root"},
    }
}

NON_COMPLIANT = {
    "dev#d1234_batch": {  # bad folder name
        "Type": "Folder", "Application": "BadApp", "SubApplication": "", "Description": "",
        "DaysKeepActive": "45",
        "D1234_JOB": {"Type": "Job:Command", "Host": "0225_CTM_HOSTGROUP", "RunAs": "root",
                      "Description": "x"},
    }
}


def _report(obj):
    return Report(audit_tree(obj))


def test_resolution():
    assert standards.resolve_for_app("0225") == standards.BNC_CTRLM_ADMIN
    assert standards.resolve_for_app("1234") == standards.BNC_STANDARD
    assert standards.app_number("1234 - X", "") == "1234"
    assert standards.app_number("", "DEV#D0225_X") == "0225"


def test_compliant_tenant_passes():
    report = _report(COMPLIANT)
    assert report.ok, report.summary()
    assert all(f.level == PASS for f in report.findings)


def test_0225_admin_is_bypassed():
    report = _report(ADMIN_0225)
    # single bypass finding even though the job uses root + infra host
    assert report.ok
    assert any(f.rule_id == "STD_BYPASS" for f in report.findings)


def test_non_compliant_tenant_flags_each_violation():
    report = _report(NON_COMPLIANT)
    assert not report.ok
    failed_rules = {f.rule_id for f in report.failures}
    assert {"R01_FOLDER_NAME", "R02_APPLICATION", "R05_HOST", "R06_RUNAS",
            "R10_DO_INCIDENT", "R11_DAYSKEEPACTIVE"} <= failed_rules


def test_job_inherits_app_from_folder():
    # job has no Application of its own -> inherits 1234 -> full rules apply (RunAs root fails)
    obj = {"DEV#D1234_X": {"Type": "Folder", "Application": "1234 - X", "SubApplication": "S",
                           "Description": "d",
                           "D1234_J": {"Type": "Job:Command", "Host": "h", "RunAs": "root",
                                       "Description": "d", "Variables": [{"DO_INCIDENT": "k"}]}}}
    assert any(f.rule_id == "R06_RUNAS" and f.level == FAIL for f in audit_tree(obj))
