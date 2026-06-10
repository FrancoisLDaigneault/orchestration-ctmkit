import pytest

from ctmkit import naming


def test_folder_expected_name():
    assert naming.expected_name("folders", "D0225_BILLING", app="0225",
                                env_token="DEV", dist="D") == "DEV#D0225_BILLING"


def test_other_expected_name():
    assert naming.expected_name("calendars", "0225_HOLYDAY", app="0225",
                                env_token="DEV", dist="D") == "0225_HOLYDAY"


@pytest.mark.parametrize("name,ok", [
    ("DEV#D0225_BILLING", True),
    ("PRD#D4007_EOD_RUN", True),
    ("dev#D0225_billing", False),
    ("DEV#X0225_BILLING", False),
    ("DEV#D225_BILLING", False),
    ("D0225_BILLING", False),
])
def test_validate_folder_name(name, ok):
    app = "0225" if "0225" in name else "4007"
    env = name.split("#")[0] if "#" in name else "DEV"
    errs = naming.validate_name(name, kind="folders", app=app, env_token=env, dist="D")
    assert (errs == []) is ok


@pytest.mark.parametrize("name,ok", [
    ("0225_HOLYDAY", True),
    ("0225_SAP_SLOTS", True),
    ("DEV#0225_HOLYDAY", False),
    ("4007_HOLYDAY", False),
    ("0225_holyday", False),
])
def test_validate_other_name(name, ok):
    errs = naming.validate_name(name, kind="calendars", app="0225",
                                env_token="DEV", dist="D")
    assert (errs == []) is ok
