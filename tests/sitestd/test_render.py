from ctmkit.sitestd import render


def test_site_standard_has_rules_and_internal_rules():
    obj = render.site_standard()["BNC-STANDARD"]
    assert obj["Type"] == "SiteStandard"
    props = {r["Property"] for r in obj["Rules"]}
    assert {"FolderName", "JobName", "Application", "RunAs"} <= props
    assert any(ir["RuleName"] == "Prefix" for ir in obj["InternalRules"])


def test_ctrlm_admin_has_no_rules():
    obj = render.ctrlm_admin()["BNC-CTRLM-ADMIN"]
    assert obj["Type"] == "SiteStandard" and obj["Rules"] == []


def test_policies_bind_standards():
    pol = render.policies()
    assert pol["BNC-STANDARD-POLICY"]["SiteStandard"] == "BNC-STANDARD"
    assert pol["BNC-STANDARD-POLICY"]["ErrorLevel"] == "Error"
    assert pol["BNC-CTRLM-ADMIN-POLICY"]["SiteStandard"] == "BNC-CTRLM-ADMIN"


def test_all_objects_keys():
    assert set(render.all_objects()) == {"bnc-standard", "bnc-ctrlm-admin", "policies"}
