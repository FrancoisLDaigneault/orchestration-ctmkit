from pathlib import Path

from ctmkit.schema import validate_object

SCHEMAS = Path(__file__).parent / "fixtures" / "schemas"


def test_valid_calendar_passes():
    obj = {"0225_HOLYDAY": {"Type": "Calendar"}}
    assert validate_object(obj, "calendars", SCHEMAS) == []


def test_invalid_calendar_reports_error():
    obj = {"0225_HOLYDAY": {"Type": "WrongType"}}
    errs = validate_object(obj, "calendars", SCHEMAS)
    assert errs and "Type" in errs[0]
