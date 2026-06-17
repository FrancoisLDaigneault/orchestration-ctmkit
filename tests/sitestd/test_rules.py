from ctmkit.sitestd import rules
from ctmkit.sitestd.rules import FAIL, PASS, WARN


def test_folder_name():
    assert rules.folder_name("DEV#D1234_BATCH_DAILY").level == PASS
    assert rules.folder_name("dev#d1234_batch").level == FAIL
    assert rules.folder_name("D1234_BATCH").level == FAIL  # missing #


def test_sub_folder_name():
    assert rules.sub_folder_name("D1234_SF_STEP1").level == PASS
    assert rules.sub_folder_name("D1234_STEP1").level == FAIL


def test_application():
    assert rules.application({"Application": "1234 - Comptes"}).level == PASS
    assert rules.application({"Application": "MonApp"}).level == FAIL


def test_job_name_standard_as400_io_and_sf():
    assert rules.job_name("D1234_EXTRACT", "Job:Command", "host").level == PASS
    assert rules.job_name("d1234_extract", "Job:Command", "host").level == FAIL
    assert rules.job_name("I5678_RPRT", "Job:OS400 Multiple Commands", "h").level == PASS
    assert rules.job_name("WAY_TOO_LONG_NAME", "Job:OS400 Multiple Commands", "h").level == FAIL
    assert rules.job_name("anything_here", "Job:Command", "iopap01").level == PASS  # IO host
    assert rules.job_name("D1234_SF_X", "Job:Command", "host").level == FAIL  # _SF_ forbidden


def test_host_excludes_infra():
    assert rules.host({"Host": "appHost"}).level == PASS
    assert rules.host({"Host": "0225_CTM_HOSTGROUP"}).level == FAIL
    assert rules.host({"Host": "lrpccctrlmctm1"}).level == FAIL
    assert rules.host({}).level == FAIL  # required


def test_run_as_forbidden_and_mft_skip():
    assert rules.run_as({"RunAs": "svc_app"}, "1234 - X").level == PASS
    assert rules.run_as({"RunAs": "root"}, "1234 - X").level == FAIL
    assert rules.run_as({"RunAs": "r00t"}, "1234 - X").level == FAIL
    assert rules.run_as({"RunAs": "root"}, "4007 - MFT") is None  # MFT exempt


def test_do_incident_required_and_exemptions():
    job = {"Variables": [{"DO_INCIDENT": "1234_X"}]}
    assert rules.do_incident("D1234_JOB", job).level == PASS
    assert rules.do_incident("D1234_JOB", {}).level == FAIL
    assert rules.do_incident("D1234_FLOW#STEP", {}) is None  # '#' exempt
    assert rules.do_incident("D1234_SF_X", {}) is None  # '_SF_' exempt


def test_days_keep_active():
    assert rules.days_keep_active({"DaysKeepActive": "3"}).level == PASS
    assert rules.days_keep_active({"DaysKeepActive": "45"}).level == FAIL
    assert rules.days_keep_active({}) is None


def test_calendars_and_events():
    cals = rules.calendars({"RuleBasedCalendars": ["D1234_WDY", "!D1234_HOLIDAYS", "bad"]})
    assert [c.level for c in cals] == [PASS, PASS, FAIL]
    evs = rules.events({"eventsToAdd": {"Type": "AddEvents", "Events": [
        {"Event": "D1234_A-TO-D1234_B"}, {"Event": "D1234_*"}]}})
    assert [e.level for e in evs] == [PASS, FAIL]


def test_controlm_server_warns_on_unknown():
    assert rules.controlm_server({"ControlmServer": "DEV"}).level == PASS
    assert rules.controlm_server({"ControlmServer": "WAT"}).level == WARN
