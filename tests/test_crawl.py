"""Unit tests for crawl hierarchy/title helpers (no network)."""
from ctmkit.docs import crawl


def test_relpath_groups_api_by_prefix():
    assert crawl.relpath_for("API", "API_CodeRef_Folder") == "code-reference/Folder.md"
    assert crawl.relpath_for("API", "API_Services_DeployService") == "services/DeployService.md"
    assert crawl.relpath_for("API", "API_Tutorials_Main") == "tutorials/Main.md"
    assert crawl.relpath_for("API", "API_Intro") == "API_Intro.md"


def test_relpath_k8s_and_9022():
    assert crawl.relpath_for("K8S", "K8S_Overview") == "Overview.md"
    assert crawl.relpath_for("9.0.22", "AI_Jett") == "application-integrator/Jett.md"
    assert crawl.relpath_for("9.0.22", "Calendars") == "Calendars.md"


def test_page_name_and_title():
    assert crawl.page_name("https://x/y/API_Intro.htm") == "API_Intro"
    assert crawl.get_title("<h1>Deploy <b>Service</b></h1>", "fb") == "Deploy Service"
    assert crawl.get_title("<title>Folders - BMC Documentation</title>", "fb") == "Folders"
    assert crawl.get_title("<p>no heading</p>", "fallback") == "fallback"
